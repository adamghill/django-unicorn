import copy
import logging
from functools import wraps
from typing import Dict, Sequence

from django.core.cache import caches
from django.forms import ValidationError
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponseNotModified
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import orjson
from bs4 import BeautifulSoup

from django_unicorn.components import UnicornView
from django_unicorn.components.unicorn_template_response import get_root_element
from django_unicorn.decorators import timed
from django_unicorn.errors import RenderNotModified, UnicornCacheError, UnicornViewError
from django_unicorn.serializer import loads
from django_unicorn.settings import (
    get_cache_alias,
    get_serial_enabled,
    get_serial_timeout,
)
from django_unicorn.utils import generate_checksum, CacheableComponent
from django_unicorn.views.action_parsers import call_method, sync_input
from django_unicorn.views.objects import ComponentRequest
from django_unicorn.views.utils import set_property_from_data


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handle_error(view_func):
    """
    Returns a JSON response with an error if necessary.
    """

    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except UnicornViewError as e:
            return JsonResponse({"error": str(e)})
        except RenderNotModified:
            return HttpResponseNotModified()
        except AssertionError as e:
            return JsonResponse({"error": str(e)})

    return wraps(view_func)(wrapped_view)


def _process_component_request(
    request: HttpRequest, component_request: ComponentRequest
) -> Dict:
    """
    Process a `ComponentRequest`:
        1. construct a Component view
        2. set all of the properties on the view from the data
        3. execute the type
            - update the properties based on the payload for "syncInput"
            - call the method specified for "callMethod"
        4. validate any fields specified in a Django form
        5. construct a `dict` that will get returned in a `JsonResponse` later on

    Args:
        param request: HttpRequest for the function-based view.
        param: component_request: Component request to process.

    Returns:
        `dict` with the following structure:
        {
            "id": component_id,
            "dom": html,  // re-rendered version of the component after actions in the payload are completed
            "data": {},  // updated data after actions in the payload are completed
            "errors": {},  // form validation errors
            "return": {}, // optional return value from an executed action
            "parent": {},  // optional representation of the parent component
        }
    """
    component = UnicornView.create(
        component_id=component_request.id,
        component_name=component_request.name,
        request=request,
    )

    # This shouldn't happen, but is a fail-safe to make sure that there is always a request on the component
    if component.request is None:
        component.request = request

    # Get a deepcopy of the data passed in to determine what fields are updated later
    original_data = copy.deepcopy(component_request.data)

    # Set component properties based on request data
    for (property_name, property_value) in component_request.data.items():
        set_property_from_data(component, property_name, property_value)
    component.hydrate()

    validate_all_fields = False
    is_reset_called = False
    is_refresh_called = False
    return_data = None
    partials = []

    for action in component_request.action_queue:
        if action.partial:
            partials.append(action.partial)
        else:
            partials = action.partials

        if action.action_type == "syncInput":
            sync_input.handle(component_request, component, action.payload)
        elif action.action_type == "callMethod":
            try:
                (
                    component,
                    _is_refresh_called,
                    _is_reset_called,
                    _validate_all_fields,
                    return_data,
                ) = call_method.handle(component_request, component, action.payload)

                is_refresh_called = is_refresh_called | _is_refresh_called
                is_reset_called = is_reset_called | _is_reset_called
                validate_all_fields = validate_all_fields | _validate_all_fields
            except ValidationError as e:
                assert not hasattr(
                    e, "error_list"
                ), "ValidationError must be instantiated with a dictionary"

                for field, message in e.message_dict.items():
                    assert e.args[1], "Error code must be specified"
                    error_code = e.args[1]

                    if field in component.errors:
                        component.errors[field].append(
                            {"code": error_code, "message": message}
                        )
                    else:
                        component.errors[field] = [
                            {"code": error_code, "message": message}
                        ]
        else:
            raise UnicornViewError(f"Unknown action_type '{action.action_type}'")

    component.complete()

    # Re-load frontend context variables to deal with non-serializable properties
    component_request.data = orjson.loads(component.get_frontend_context_variables())

    # Get set of attributes that should be marked as `safe`
    safe_fields = []
    if hasattr(component, "Meta") and hasattr(component.Meta, "safe"):
        if isinstance(component.Meta.safe, Sequence):
            for field_name in component.Meta.safe:
                if field_name in component._attributes().keys():
                    safe_fields.append(field_name)

    # Mark safe attributes as such before rendering
    for field_name in safe_fields:
        value = getattr(component, field_name)
        if isinstance(value, str):
            setattr(component, field_name, mark_safe(value))

    # Send back all available data for reset or refresh actions
    updated_data = component_request.data

    if not is_reset_called:
        if not is_refresh_called:
            updated_data = {}

            for key, value in original_data.items():
                if value != component_request.data.get(key):
                    updated_data[key] = component_request.data.get(key)

        if validate_all_fields:
            component.validate()
        else:
            component.validate(model_names=list(updated_data.keys()))

    request_queued_messages = []

    if return_data and return_data.redirect and "url" in return_data.redirect:
        # If we know the user wants to redirect, get a copy of the private queued messages
        # and make sure they get stored for the next page load instead of getting rendered
        # by the component
        try:
            request_queued_messages = copy.deepcopy(
                component.request._messages._queued_messages
            )
            component.request._messages._queued_messages = []
        except AttributeError as e:
            logger.warning(e)

    # Pass the current request so that it can be used inside the component template
    rendered_component = component.render(request=request)
    component.rendered(rendered_component)

    if request_queued_messages:
        try:
            component.request._messages._queued_messages = request_queued_messages
        except AttributeError as e:
            logger.warning(e)

    cache = caches[get_cache_alias()]

    try:
        with CacheableComponent(component):
            cache.set(component.component_cache_key, component)
    except UnicornCacheError as e:
        logger.warning(e)

    partial_doms = []

    if partials and all(partials):
        soup = BeautifulSoup(rendered_component, features="html.parser")

        for partial in partials:
            partial_found = False
            only_id = False
            only_key = False

            target = partial.get("target")

            if not target:
                target = partial.get("key")

                if target:
                    only_key = True

            if not target:
                target = partial.get("id")

                if target:
                    only_id = True

            assert target, "Partial target is required"

            if not only_id:
                for element in soup.find_all():
                    if (
                        "unicorn:key" in element.attrs
                        and element.attrs["unicorn:key"] == target
                    ):
                        partial_doms.append({"key": target, "dom": str(element)})
                        partial_found = True
                        break

            if not partial_found and not only_key:
                for element in soup.find_all():
                    if "id" in element.attrs and element.attrs["id"] == target:
                        partial_doms.append({"id": target, "dom": str(element)})
                        partial_found = True
                        break

    res = {
        "id": component_request.id,
        "data": updated_data,
        "errors": component.errors,
        "calls": component.calls,
        "checksum": generate_checksum(str(component_request.data)),
    }

    if partial_doms:
        res.update({"partials": partial_doms})
    else:
        hash = generate_checksum(rendered_component)

        if (
            component_request.hash == hash
            and (not return_data or not return_data.value)
            and not component.calls
        ):
            raise RenderNotModified()

        # Make sure that partials with comments or blank lines before the root element only return the root element
        soup = BeautifulSoup(rendered_component, features="html.parser")
        rendered_component = str(get_root_element(soup))

        res.update(
            {
                "dom": rendered_component,
                "hash": hash,
            }
        )

    if return_data:
        res.update(
            {
                "return": return_data.get_data(),
            }
        )

        if return_data.redirect:
            res.update(
                {
                    "redirect": return_data.redirect,
                }
            )

        if return_data.poll:
            res.update(
                {
                    "poll": return_data.poll,
                }
            )

    parent_component = component.parent
    parent_res = res

    while parent_component:
        # TODO: Should parent_component.hydrate() be called?
        parent_frontend_context_variables = loads(
            parent_component.get_frontend_context_variables()
        )
        parent_checksum = generate_checksum(str(parent_frontend_context_variables))

        parent = {
            "id": parent_component.component_id,
            "checksum": parent_checksum,
        }

        if not partial_doms:
            parent_dom = parent_component.render()
            component.parent_rendered(parent_dom)

            try:

                with CacheableComponent(parent_component):
                    cache.set(
                        parent_component.component_cache_key,
                        parent_component,
                    )
            except UnicornCacheError as e:
                logger.warning(e)

            parent.update(
                {
                    "dom": parent_dom,
                    "data": parent_frontend_context_variables,
                    "errors": parent_component.errors,
                }
            )

        parent_res.update({"parent": parent})
        component = parent_component
        parent_component = parent_component.parent
        parent_res = parent

    return res


def _handle_component_request(
    request: HttpRequest, component_request: ComponentRequest
) -> Dict:
    """
    Process a `ComponentRequest` by adding it to the cache and then either:
        - processing all of the component requests in the cache and returning the resulting value if
            it is the first component request for that particular component name + component id combination
        - return a `dict` saying that the request has been queued

    Args:
        param request: HttpRequest for the function-based view.
        param: component_request: Component request to process.

    Returns:
        `dict` with the following structure:
        {
            "id": component_id,
            "dom": html,  // re-rendered version of the component after actions in the payload are completed
            "data": {},  // updated data after actions in the payload are completed
            "errors": {},  // form validation errors
            "return": {}, // optional return value from an executed action
            "parent": {},  // optional representation of the parent component
        }
    """
    # If serial isn't enabled or the wrong cache, just process the request like normal
    if not get_serial_enabled():
        return _process_component_request(request, component_request)

    cache = caches[get_cache_alias()]

    # Add the current request `ComponentRequest` to the cache
    queue_cache_key = f"unicorn:queue:{component_request.id}"
    component_requests = cache.get(queue_cache_key) or []

    # Remove `request` from `ComponentRequest` before caching because it is not pickleable
    component_request.request = None
    component_requests.append(component_request)

    cache.set(
        queue_cache_key,
        component_requests,
        timeout=get_serial_timeout(),
    )

    if len(component_requests) > 1:
        original_epoch = component_requests[0].epoch
        return {
            "queued": True,
            "epoch": component_request.epoch,
            "original_epoch": original_epoch,
        }

    return _handle_queued_component_requests(
        request, component_request.name, queue_cache_key
    )


def _handle_queued_component_requests(
    request: HttpRequest, component_name: str, queue_cache_key
) -> Dict:
    """
    Process the current component requests that are stored in cache.
    Also recursively checks for new requests that might have happened
    while executing the first request, merges them together and returns
    the correct appropriate data.

    Args:
        param request: HttpRequest for the view.
        param: component_name: Name of the component, e.g. "hello-world".
        param: queue_cache_key: Cache key created from component id which should be unique
            for any particular user's request lifecycle.

    Returns:
        JSON with the following structure:
        {
            "id": component_id,
            "dom": html,  // re-rendered version of the component after actions in the payload are completed
            "data": {},  // updated data after actions in the payload are completed
            "errors": {},  // form validation errors
            "return": {}, // optional return value from an executed action
            "parent": {},  // optional representation of the parent component
        }
    """
    cache = caches[get_cache_alias()]

    # Handle current request and any others in the cache by first sorting all of the current requests by ascending order
    component_requests = cache.get(queue_cache_key)

    if not component_requests or not isinstance(component_requests, list):
        raise UnicornViewError(f"No request found for {queue_cache_key}")

    component_requests = sorted(component_requests, key=lambda r: r.epoch)
    first_component_request = component_requests[0]

    try:
        # Can't store request on a `ComponentRequest` and cache it because `HttpRequest` isn't pickleable
        first_json_result = _process_component_request(request, first_component_request)
    except RenderNotModified:
        # Catching this and re-raising, but need the finally clause to clear the cache
        raise
    finally:
        # Re-check for requests after the first request is processed
        component_requests = cache.get(queue_cache_key)

        # Check that the request is in the cache before popping it off
        if component_requests:
            component_requests.pop(0)
            cache.set(
                queue_cache_key,
                component_requests,
                timeout=get_serial_timeout(),
            )

    if component_requests:
        # Create one new `component_request` from all of the queued requests that can be processed
        merged_component_request = None

        for additional_component_request in copy.deepcopy(component_requests):
            if merged_component_request:
                # Add new component request action queue to the merged component request
                merged_component_request.action_queue.extend(
                    additional_component_request.action_queue
                )

                # Originally, the thought was to merge the `additional_component_request.data` into
                # the `merged_component_request.data`, but I can't figure out a way to do that in a sane
                # manner. This means that for rapidly fired events that mutate `data`, that new
                # `data` with be "thrown away".
                # Relevant test: test_call_method_multiple.py::test_message_call_method_multiple_with_updated_data
            else:
                merged_component_request = additional_component_request

                # Set new component request data from the first component request's resulting data
                for key, val in first_json_result.get("data", {}).items():
                    merged_component_request.data[key] = val

            component_requests.pop(0)
            cache.set(
                queue_cache_key,
                component_requests,
                timeout=get_serial_timeout(),
            )

        merged_json_result = _handle_component_request(
            request, merged_component_request
        )

        return merged_json_result

    return first_json_result


@timed
@handle_error
@csrf_protect
@require_POST
def message(request: HttpRequest, component_name: str = None) -> JsonResponse:
    """
    Endpoint that instantiates the component and does the correct action
    (set an attribute or call a method) depending on the JSON payload in the body.

    Args:
        param request: HttpRequest for the function-based view.
        param: component_name: Name of the component, e.g. "hello-world".

    Returns:
        `JsonRequest` with the following structure in the body:
        {
            "id": component_id,
            "dom": html,  // re-rendered version of the component after actions in the payload are completed
            "data": {},  // updated data after actions in the payload are completed
            "errors": {},  // form validation errors
            "return": {}, // optional return value from an executed action
            "parent": {},  // optional representation of the parent component
        }
    """

    assert component_name, "Missing component name in url"

    component_request = ComponentRequest(request, component_name)
    json_result = _handle_component_request(request, component_request)

    return JsonResponse(json_result, json_dumps_params={"separators": (",", ":")})
