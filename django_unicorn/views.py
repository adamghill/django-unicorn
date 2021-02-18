import copy
import logging
from dataclasses import is_dataclass
from functools import wraps
from typing import Any, Dict, List, Union, get_type_hints

from django.core.cache import caches
from django.db.models import Model
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import orjson
from bs4 import BeautifulSoup
from cachetools.lru import LRUCache

from .call_method_parser import InvalidKwarg, parse_call_method_name, parse_kwarg
from .components import UnicornField, UnicornView
from .decorators import timed
from .errors import UnicornViewError
from .message import ComponentRequest, Return
from .serializer import dumps, loads
from .settings import get_cache_alias, get_serial_enabled, get_serial_timeout
from .utils import generate_checksum


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


type_hints_cache = LRUCache(maxsize=100)


def handle_error(view_func):
    """
    Returns a JSON response with an error if necessary.
    """

    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except UnicornViewError as e:
            return JsonResponse({"error": str(e)})
        except AssertionError as e:
            return JsonResponse({"error": str(e)})

    return wraps(view_func)(wrapped_view)


def _get_type_hints(obj):
    """
    Get type hints from an object. These get cached in a local memory cache for quicker look-up later.

    Returns:
        An empty dictionary if no type hints can be retrieved.
    """
    try:
        if obj in type_hints_cache:
            return type_hints_cache[obj]
    except TypeError:
        # Ignore issues with checking for an object in the cache, e.g. when a Django model is missing a PK
        pass

    try:
        type_hints = get_type_hints(obj)

        # Cache the type hints just in case
        type_hints_cache[obj] = type_hints

        return type_hints
    except TypeError:
        #  Return an empty dictionary when there is a TypeError. From `get_type_hints`: "TypeError is
        # raised if the argument is not of a type that can contain annotations, and an empty dictionary
        # is returned if no annotations are present"
        return {}


@timed
def _is_component_field_model_or_unicorn_field(
    component_or_field: Union[UnicornView, UnicornField, Model], name: str,
) -> bool:
    """
    Determines whether a component's field is a Django `Model` or `UnicornField` either
    by checking the field's instance or inspecting the type hints.

    One side-effect is that the field will be instantiated if it is currently `None` and
    the type hint is available.

    Args:
        component: `UnicornView` to check.
        name: Name of the field.

    Returns:
        Whether the field is a Django `Model` or `UnicornField`.
    """
    field = getattr(component_or_field, name)

    if isinstance(field, UnicornField) or isinstance(field, Model):
        return True

    is_subclass_of_model = False
    is_subclass_of_unicorn_field = False
    component_type_hints = {}

    try:
        component_type_hints = _get_type_hints(component_or_field)

        if name in component_type_hints:
            is_subclass_of_model = issubclass(component_type_hints[name], Model)

            if not is_subclass_of_model:
                is_subclass_of_unicorn_field = issubclass(
                    component_type_hints[name], UnicornField
                )

            # Construct a new class if the field is None and there is a type hint available
            if field is None:
                if is_subclass_of_model or is_subclass_of_unicorn_field:
                    field = component_type_hints[name]()
                    setattr(component_or_field, name, field)
    except TypeError:
        pass

    return is_subclass_of_model or is_subclass_of_unicorn_field


@timed
def _set_property_from_data(
    component_or_field: Union[UnicornView, UnicornField, Model], name: str, value: Any,
) -> None:
    """
    Sets properties on the component based on passed-in data.
    """

    if not hasattr(component_or_field, name):
        return

    field = getattr(component_or_field, name)
    component_field_is_model_or_unicorn_field = _is_component_field_model_or_unicorn_field(
        component_or_field, name
    )

    # UnicornField and Models are always a dictionary (can be nested)
    if component_field_is_model_or_unicorn_field:
        # Re-get the field since it might have been set in `_is_component_field_model_or_unicorn_field`
        field = getattr(component_or_field, name)

        if isinstance(value, dict):
            for key in value.keys():
                key_value = value[key]
                _set_property_from_data(field, key, key_value)
        else:
            _set_property_from_data(field, field.name, value)
    else:
        type_hints = _get_type_hints(component_or_field)

        if name in type_hints:
            # Construct the specified type by passing the value in
            # Usually the value will be a string (because it is coming from JSON)
            # and basic types can be constructed by passing in a string,
            # i.e. int("1") or float("1.1")

            if is_dataclass(type_hints[name]):
                value = type_hints[name](**value)
            else:
                value = type_hints[name](value)

        if hasattr(component_or_field, "_set_property"):
            # Can assume that `component_or_field` is a component
            component_or_field._set_property(name, value)
        else:
            setattr(component_or_field, name, value)


@timed
def _set_property_value(
    component: UnicornView, property_name: str, property_value: Any, data: Dict = {}
) -> None:
    """
    Sets properties on the component.
    Also updates the data dictionary which gets set back as part of the payload.

    Args:
        param component: Component to set attributes on.
        param property_name: Name of the property.
        param property_value: Value to set on the property.
        param data: Dictionary that gets sent back with the response. Defaults to {}.
    """

    assert property_name is not None, "Property name is required"
    assert property_value is not None, "Property value is required"

    component.updating(property_name, property_value)

    """
    Handles nested properties. For example, for the following component:

    class Author(UnicornField):
        name = "Neil"

    class TestView(UnicornView):
        author = Author()
    
    `payload` would be `{'name': 'author.name', 'value': 'Neil Gaiman'}`

    The following code updates UnicornView.author.name based the payload's `author.name`.
    """
    property_name_parts = property_name.split(".")
    component_or_field = component
    data_or_dict = data  # Could be an internal portion of data that gets set

    for (idx, property_name_part) in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                if hasattr(component_or_field, "_set_property"):
                    # Can assume that `component_or_field` is a component
                    component_or_field._set_property(property_name_part, property_value)
                else:
                    # Handle calling the updating/updated method for nested properties
                    property_name_snake_case = property_name.replace(".", "_")
                    updating_function_name = f"updating_{property_name_snake_case}"
                    updated_function_name = f"updated_{property_name_snake_case}"

                    if hasattr(component, updating_function_name):
                        getattr(component, updating_function_name)(property_value)

                    setattr(component_or_field, property_name_part, property_value)

                    if hasattr(component, updated_function_name):
                        getattr(component, updated_function_name)(property_value)

                data_or_dict[property_name_part] = property_value
            else:
                component_or_field = getattr(component_or_field, property_name_part)
                data_or_dict = data_or_dict.get(property_name_part, {})
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                component_or_field[property_name_part] = property_value
                data_or_dict[property_name_part] = property_value
            else:
                component_or_field = component_or_field[property_name_part]
                data_or_dict = data_or_dict.get(property_name_part, {})

    component.updated(property_name, property_value)


@timed
def _get_property_value(component: UnicornView, property_name: str) -> Any:
    """
    Gets property value from the component based on the property name.
    Handles nested property names.

    Args:
        param component: Component to get property values from.
        param property_name: Property name. Can be "dot-notation" to get nested properties.
    """

    assert property_name is not None, "property_name name is required"

    # Handles nested properties
    property_name_parts = property_name.split(".")
    component_or_field = component

    for (idx, property_name_part) in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                return getattr(component_or_field, property_name_part)
            else:
                component_or_field = getattr(component_or_field, property_name_part)
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                return component_or_field[property_name_part]
            else:
                component_or_field = component_or_field[property_name_part]


@timed
def _call_method_name(
    component: UnicornView, method_name: str, args: List[Any], kwargs: Dict[str, Any]
) -> Any:
    """
    Calls the method name with parameters.

    Args:
        param component: Component to call method on.
        param method_name: Method name to call.
        param args: List of arguments for the method.
        param kwargs: Dictionary of kwargs for the method.
    """

    if method_name is not None and hasattr(component, method_name):
        func = getattr(component, method_name)

        if args and kwargs:
            return func(*args, **kwargs)
        elif args:
            return func(*args, **kwargs)
        elif kwargs:
            return func(**kwargs)
        else:
            return func()


def _process_component_request(
    request: HttpRequest, component_request: ComponentRequest
) -> Dict:
    """
    Process a `ComponentRequest` by:
        1. construct a Component view
        2. set all of the properties on the view from the data
        3. execute the type
            - update the properties based on the payload for "syncInput"
            - create/update the Django Model based on the payload for "dbInput"
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
    validate_all_fields = False

    # Get a deepcopy of the data passed in to determine what fields are updated later
    original_data = copy.deepcopy(component_request.data)

    # Set component properties based on request data
    for (property_name, property_value) in component_request.data.items():
        _set_property_from_data(component, property_name, property_value)
    component.hydrate()

    is_reset_called = False
    is_refresh_called = False
    return_data = None
    partials = []

    for action in component_request.action_queue:
        action_type = action.get("type")
        payload = action.get("payload", {})
        partials.append(action.get("partial"))

        if action_type == "syncInput":
            property_name = payload.get("name")
            property_value = payload.get("value")
            _set_property_value(
                component, property_name, property_value, component_request.data
            )
        elif action_type == "dbInput":
            model = payload.get("model")
            db = payload.get("db", {})
            db_model_name = db.get("name")
            pk = db.get("pk")

            DbModel = None
            db_defaults = {}

            if model:
                model_class = getattr(component, model)

                if hasattr(model_class, "model"):
                    DbModel = model_class.model

                    if hasattr(component, "Meta"):
                        for m in component.Meta.db_models:
                            if m.model_class == model_class.model:
                                db_defaults = m.defaults
                                break

            if not DbModel and db_model_name:
                assert hasattr(component, "Meta") and hasattr(
                    component.Meta, "db_models"
                ), f"Missing Meta.db_models list in component"

                for m in component.Meta.db_models:
                    if m.name == db_model_name:
                        DbModel = m.model_class
                        db_defaults = m.defaults
                        break

            fields = payload.get("fields", {})

            assert (
                DbModel
            ), f"Missing {model}.model and {db_model_name} in Meta.db_models"
            assert issubclass(
                DbModel, Model
            ), "Model must be an instance of `django.db.models.Model"

            if fields:
                fields_to_update = db_defaults
                fields_to_update.update(fields)

                if pk:
                    DbModel.objects.filter(pk=pk).update(**fields_to_update)
                else:
                    instance = DbModel(**fields_to_update)
                    instance.save()
                    pk = instance.pk
        elif action_type == "callMethod":
            call_method_name = payload.get("name", "")
            assert call_method_name, "Missing 'name' key for callMethod"

            (method_name, args, kwargs) = parse_call_method_name(call_method_name)
            return_data = Return(method_name, args, kwargs)
            setter_method = {}

            if "=" in call_method_name:
                try:
                    setter_method = parse_kwarg(
                        call_method_name, raise_if_unparseable=True
                    )
                except InvalidKwarg:
                    pass

            if setter_method:
                property_name = list(setter_method.keys())[0]
                property_value = setter_method[property_name]

                _set_property_value(component, property_name, property_value)
                return_data = Return(property_name, [property_value])
            else:
                if method_name == "$refresh":
                    # Handle the refresh special action
                    component = UnicornView.create(
                        component_id=component_request.id,
                        component_name=component_request.name,
                        request=request,
                    )

                    # Set component properties based on request data
                    for (
                        property_name,
                        property_value,
                    ) in component_request.data.items():
                        _set_property_from_data(
                            component, property_name, property_value
                        )
                    component.hydrate()

                    is_refresh_called = True
                elif method_name == "$reset":
                    # Handle the reset special action
                    component = UnicornView.create(
                        component_id=component_request.id,
                        component_name=component_request.name,
                        request=request,
                        use_cache=False,
                    )

                    #  Explicitly remove all errors and prevent validation from firing before render()
                    component.errors = {}
                    is_reset_called = True
                elif method_name == "$toggle":
                    for property_name in args:
                        property_value = _get_property_value(component, property_name)
                        property_value = not property_value

                        _set_property_value(component, property_name, property_value)
                elif method_name == "$validate":
                    # Handle the validate special action
                    validate_all_fields = True
                else:
                    component.calling(method_name, args)
                    return_data.value = _call_method_name(
                        component, method_name, args, kwargs
                    )
                    component.called(method_name, args)
        else:
            raise UnicornViewError(f"Unknown action_type '{action_type}'")

    component.complete()

    # Re-load frontend context variables to deal with non-serializable properties
    component_request.data = orjson.loads(component.get_frontend_context_variables())

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

    rendered_component = component.render()
    component.rendered(rendered_component)

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
        "checksum": generate_checksum(orjson.dumps(component_request.data)),
    }

    if partial_doms:
        res.update({"partials": partial_doms})
    else:
        res.update({"dom": rendered_component})

    if return_data:
        res.update(
            {"return": return_data.get_data(),}
        )

        if return_data.redirect:
            res.update(
                {"redirect": return_data.redirect,}
            )

        if return_data.poll:
            res.update(
                {"poll": return_data.poll,}
            )

    parent_component = component.parent

    if parent_component:
        parent_frontend_context_variables = loads(
            parent_component.get_frontend_context_variables()
        )
        parent_checksum = generate_checksum(dumps(parent_frontend_context_variables))

        parent = {
            "id": parent_component.component_id,
            "checksum": parent_checksum,
        }

        if not partial_doms:
            parent_dom = parent_component.render()
            component.parent_rendered(parent_dom)

            parent.update(
                {
                    "dom": parent_dom,
                    "data": parent_frontend_context_variables,
                    "errors": parent_component.errors,
                }
            )

        res.update({"parent": parent})

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
    component_cache_key = (
        f"unicorn:queue:{component_request.name}:{component_request.id}"
    )
    component_requests = cache.get(component_cache_key) or []
    component_requests.append(component_request)

    cache.set(
        component_cache_key, component_requests, timeout=get_serial_timeout(),
    )

    if len(component_requests) > 1:
        original_epoch = component_requests[0].epoch
        return {
            "queued": True,
            "epoch": component_request.epoch,
            "original_epoch": original_epoch,
        }

    return _handle_queued_component_requests(
        request, component_request.name, component_cache_key
    )


def _handle_queued_component_requests(
    request: HttpRequest, component_name: str, component_cache_key
) -> Dict:
    """
    Process the current component requests that are stored in cache.
    Also recursively checks for new requests that might have happened
    while executing the first request, merges them together and returns
    the correct appropriate data.

    Args:
        param request: HttpRequest for the view.
        param: component_name: Name of the component, e.g. "hello-world".
        param: component_cache_key: Cache key created from name of the component and the
            component id which should be unique for any particular user's request lifecycle.
    
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
    component_requests = cache.get(component_cache_key)

    if not component_requests or not isinstance(component_requests, list):
        raise UnicornViewError(f"No request found for {component_cache_key}")

    component_requests = sorted(component_requests, key=lambda r: r.epoch)
    first_component_request = component_requests[0]

    # Can't store request on a `ComponentRequest` and cache it because `HttpRequest`
    # isn't pickleable. Does it matter that a different request gets passed in then
    # the original request that generated the `ComponentRequest`?
    first_json_result = _process_component_request(request, first_component_request)

    # Re-check for requests after the first request is processed
    component_requests = cache.get(component_cache_key)

    # Check that the request is in the cache before popping it off
    if component_requests:
        component_requests.pop(0)
        cache.set(
            component_cache_key, component_requests, timeout=get_serial_timeout(),
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
                component_cache_key, component_requests, timeout=get_serial_timeout(),
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

    return JsonResponse(json_result)
