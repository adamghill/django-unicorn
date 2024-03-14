import logging

import copy
from django.http import JsonResponse, HttpResponseRedirect
from bs4 import BeautifulSoup, Tag

from django_unicorn.components.unicorn_template_response import get_root_element
from django_unicorn.components import HashUpdate, LocationUpdate, PollUpdate
from django_unicorn.errors import UnicornViewError, RenderNotModifiedError
from django_unicorn.serializer import JSONDecodeError, dumps, loads
from django_unicorn.utils import generate_checksum, is_int

logger = logging.getLogger(__name__)


class Action:
    """
    Action that gets queued.
    """

    def __init__(self, data):
        self.action_type = data.get("type")
        self.payload = data.get("payload", {})
        self.partial = data.get("partial")  # this is deprecated, but leaving it for now
        self.partials = data.get("partials", [])

    def __repr__(self):
        return f"Action(action_type='{self.action_type}' payload={self.payload} partials={self.partials})"


def sort_dict(d):
    items = [
        [k, v]
        for k, v in sorted(
            d.items(), key=lambda x: x[0] if not is_int(x[0]) else int(x[0])
        )
    ]

    for item in items:
        if isinstance(item[1], dict):
            item[1] = sort_dict(item[1])

    return dict(items)


class ComponentRequest:
    """
    Parses, validates, and stores all of the data from the message request.
    """

    def __init__(self, request, component_name):
        self.body = {}
        self.request = request

        try:
            self.body = loads(request.body)

            if not self.body:
                raise AssertionError("Invalid JSON body")
        except JSONDecodeError as e:
            raise UnicornViewError("Body could not be parsed") from e

        self.name = component_name
        if not self.name:
            raise AssertionError("Missing component name")

        self.data = self.body.get("data")
        if not self.data is not None:
            raise AssertionError("Missing data")  # data could theoretically be {}

        self.id = self.body.get("id")
        if not self.id:
            raise AssertionError("Missing component id")

        self.epoch = self.body.get("epoch", "")
        if not self.epoch:
            raise AssertionError("Missing epoch")

        self.key = self.body.get("key", "")
        self.hash = self.body.get("hash", "")

        self.validate_checksum()

        self.action_queue = []
        for action_data in self.body.get("actionQueue", []):
            self.action_queue.append(Action(action_data))

        # This is populated when `apply_to_component` is called.
        # `UnicornView.update_from_component_request` will also populate it.
        # It will have the same length as `self.action_queue` and map accordingly
        self.action_results = []

    def __repr__(self):
        return (
            f"ComponentRequest(name='{self.name}' id='{self.id}' key='{self.key}'"
            f" epoch={self.epoch} data={self.data} action_queue={self.action_queue} hash={self.hash})"
        )

    @property
    def has_been_applied(self) -> bool:
        """
        Whether this ComponentRequest and it's action_queue has been applied
        to a UnicornView component.
        """
        return True if self.action_results else False

    @property
    def has_action_results(self) -> bool:
        """
        Whether any return values in `action_results` need to be handled
        """
        if not self.has_been_applied:
            raise ValueError(
                "This ComponentRequest has not been applied yet, so "
                "no action_results are unavailable."
            )
        return True if any(self.action_results) else False

    def validate_checksum(self):
        """
        Validates that the checksum in the request matches the data.

        Returns:
            Raises `AssertionError` if the checksums don't match.
        """
        checksum = self.body.get("checksum")

        if not checksum:
            # TODO: Raise specific exception
            raise AssertionError("Missing checksum")

        generated_checksum = generate_checksum(self.data)

        if checksum != generated_checksum:
            # TODO: Raise specific exception
            raise AssertionError("Checksum does not match")

    @property
    def partials(self) -> bool:
        partials = [
            partial for action in self.action_queue for partial in action.partials
        ]

        # --- depreciated --
        # remove this section when partial is removed
        for action in self.action_queue:
            if action.partial:
                partials.append(action.partial)
        # --- depreciated ---

        return partials

    @property
    def action_types(self) -> bool:
        # OPTIMIZE: consider using @cached_property
        # Also maybe deprec if `Action` subclasses are made
        return [action.action_type for action in self.action_queue]

    @property
    def is_refresh_called(self) -> bool:
        return "$refresh" in self.action_types

    @property
    def is_reset_called(self) -> bool:
        return "$reset" in self.action_types

    @property
    def validate_all_fields(self) -> bool:
        return "$validate" in self.action_types

    @property
    def is_toggled(self) -> bool:
        return "$toggle" in self.action_types

    def apply_to_component(self, component):
        # OPTIMIZE: you *could* generate the ComponentResponse obj within
        # this update method. However, intertwining this would lead to less
        # maintainable code that is much more difficult to follow/understand.
        # Therefore, we save ComponentRequest for a separate method

        from django.forms import ValidationError
        from django.core.exceptions import NON_FIELD_ERRORS

        from django_unicorn.views.utils import set_property_from_data
        from django_unicorn.views.action_parsers import call_method, sync_input
        from django_unicorn.errors import UnicornViewError

        MIN_VALIDATION_ERROR_ARGS = 2

        for property_name, property_value in self.data.items():
            set_property_from_data(component, property_name, property_value)
        component.hydrate()

        # TODO: This section needs a refactor...

        return_data = None

        for action in self.action_queue:
            if action.action_type == "syncInput":
                sync_input.handle(self, component, action.payload)
            elif action.action_type == "callMethod":
                try:
                    # TODO: continue refactor of this method
                    (
                        component,
                        return_data,
                    ) = call_method.handle(self, component, action.payload)
                    self.action_results.append(return_data)
                except ValidationError as e:
                    if len(e.args) < MIN_VALIDATION_ERROR_ARGS or not e.args[1]:
                        raise AssertionError("Error code must be specified") from e

                    if hasattr(e, "error_list"):
                        error_code = e.args[1]

                        for error in e.error_list:
                            if NON_FIELD_ERRORS in component.errors:
                                component.errors[NON_FIELD_ERRORS].append(
                                    {"code": error_code, "message": error.message}
                                )
                            else:
                                component.errors[NON_FIELD_ERRORS] = [
                                    {"code": error_code, "message": error.message}
                                ]
                    elif hasattr(e, "message_dict"):
                        for field, message in e.message_dict.items():
                            if not e.args[1]:
                                raise AssertionError(
                                    "Error code must be specified"
                                ) from e

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

        # TODO: There should be a better place to call this...
        component._mark_safe_fields()

        return return_data


class ComponentResponse:
    """
    Contains the result of changes made to a Component after a
    ComponentRequest (and its actions) have been applied to it
    """

    def __init__(self, result: dict):
        breakpoint()
        # Sort data so it's stable
        self.data = {key: result["data"][key] for key in sorted(result["data"])}

    @classmethod
    def from_inspection(cls, request, component, return_data):
        # typing: objs of ComponentRequest, Component, Return

        breakpoint()

        original_context = request.data.items()
        new_context = component.get_frontend_context()

        # inspect for special actions & pull out updated_data
        if not request.is_refresh_called:
            if not request.is_reset_called:
                # Get the context that only includes updated data
                updated_data = {
                    key: value
                    for key, value in original_context.items()
                    if new_context.get(key) != value
                }

            if request.validate_all_fields:
                component.validate()
            else:
                component.validate(model_names=list(updated_data.keys()))
        else:
            updated_data = copy(new_context.deepcopy())

        # TODO: Handle redirects and messages by patching request obj...?
        # I'm not sure what's going on here yet
        #
        # request_queued_messages = []
        # if return_data and return_data.redirect and "url" in return_data.redirect:
        #     # If we know the user wants to redirect, get a copy of the private queued messages
        #     # and make sure they get stored for the next page load instead of getting rendered
        #     # by the component
        #     try:
        #         request_queued_messages = copy.deepcopy(component.request._messages._queued_messages)
        #         component.request._messages._queued_messages = []
        #     except AttributeError as e:
        #         logger.warning(e)
        # if request_queued_messages:
        #     try:
        #         component.request._messages._queued_messages = request_queued_messages
        #     except AttributeError as e:
        #         logger.warning(e)

        # generate the html using the current request
        component_html = component.render(
            request=request,  # gives the original HttpRequest
        )

        # !!! might want to rename this hook to "post_render"... confused me at first
        # Also is there an example of when this would be used? And why it takes
        # the html as input?
        component.rendered(component_html)

        # Check if there are partials, and if so, we only want specific
        # elements of the component_html, rather than all of it
        partial_doms = cls._get_partials_from_html(
            html=component_html,
            partials=request.partials,
        )

        # base results. we add to & update this below
        result = {
            "id": request.id,
            "data": updated_data,
            "errors": component.errors,
            "calls": component.calls,
            # !!! should I checksum the request or the response data?
            "checksum": generate_checksum(request.data),
        }

        # add result from the Return object
        if return_data:
            result["return"] = return_data.get_data()
            if return_data.redirect:
                result["redirect"] = return_data.redirect
            if return_data.poll:
                result["poll"] = return_data.poll

        # --------------

        # !!! Code below needs more refactoring

        # Grab the relevant html changes in order to set "partials" or "dom"
        # and check if the html has changed at all.
        render_not_modified = False  # until proven otherwise
        if partial_doms:
            soup_root = None
            result["partials"] = partial_doms
        else:
            component_html_hash = generate_checksum(component_html)

            if (
                request.hash == component_html_hash
                and (not return_data or not return_data.value)
                and not component.calls
            ):
                if not component.parent and component.force_render is False:
                    raise RenderNotModifiedError()
                else:
                    render_not_modified = True
                    # NOTE: this can be "overturned" below when looking at parents

            # Make sure that partials with comments or blank lines before the root element
            # only return the root element
            soup = BeautifulSoup(component_html, features="html.parser")
            soup_root = get_root_element(soup)
            component_html_cleaned = str(soup_root)
            # !!! Should this be moved to the component.render method?

            result["dom"] = component_html_cleaned
            result["hash"] = component_html_hash

        # --------------

        # !!! Code below is a big shift from single to child/parent components

        # Iteratively check parent objects in can we need to update its dom instead
        # !!! what about iteratively checking children...?
        parent_component = component.parent
        parent_result = result
        while parent_component:
            if parent_component.force_render is True:
                # TODO: Should parent_component.hydrate() be called?
                parent_frontend_context_variables = loads(
                    parent_component.get_frontend_context_variables()
                )
                parent_checksum = generate_checksum(
                    str(parent_frontend_context_variables)
                )

                parent = {
                    "id": parent_component.component_id,
                    "checksum": parent_checksum,
                }

                if not partial_doms:
                    parent_dom = parent_component.render()
                    component.parent_rendered(parent_dom)

                    # Get re-generated child checksum and update the child component inside the parent DOM
                    if not soup_root:
                        raise AssertionError("Missing root element")

                    # TODO: Use minestrone for this
                    child_soup_checksum = soup_root.attrs["unicorn:checksum"]
                    child_soup_unicorn_id = soup_root.attrs["unicorn:id"]

                    parent_soup = BeautifulSoup(parent_dom, features="html.parser")

                    for _child in parent_soup.descendants:
                        if isinstance(
                            _child, Tag
                        ) and child_soup_unicorn_id == _child.attrs.get("unicorn:id"):
                            _child.attrs["unicorn:checksum"] = child_soup_checksum

                    parent_soup = get_root_element(parent_soup)
                    parent_dom = str(parent_soup)

                    # Remove the child DOM from the payload since the parent DOM supersedes it
                    result["dom"] = None

                    parent.update(
                        {
                            "dom": parent_dom,
                            "data": parent_frontend_context_variables,
                            "errors": parent_component.errors,
                            "hash": generate_checksum(parent_dom),
                        }
                    )

            if render_not_modified:
                # TODO: Determine if all parents have not changed and return a 304 if
                # that's the case
                # i.e. render_not_modified = render_not_modified and (parent hash test)
                pass

            parent_result.update({"parent": parent})
            parent_result = parent

        component = parent_component
        parent_component = parent_component.parent

        return cls(result)

    def to_json_response(self):
        breakpoint()
        return JsonResponse(
            data=self.updates,
            json_dumps_params={"separators": (",", ":")},
        )

    @staticmethod
    def _get_partials_from_html(html: str, partials: list[dict]) -> list[dict]:
        """
        Given the fully rendered html string and a list partial configs, this
        will return a list of the partial_doms (i.e. only the relevent html)
        needed, rather than the entire html.
        """

        partial_doms = []

        if partials and all(partials):
            soup = BeautifulSoup(html, features="html.parser")

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

                if not target:
                    raise AssertionError("Partial target is required")

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

        return partial_doms


class Return:
    def __init__(self, method_name, args=None, kwargs=None):
        self.method_name = method_name
        self.args = args or []
        self.kwargs = kwargs or {}
        self._value = {}
        self.redirect = {}
        self.poll = {}

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        # TODO: Support a tuple/list return_value which could contain multiple values

        if value is not None:
            if isinstance(value, HttpResponseRedirect):
                self.redirect = {
                    "url": value.url,
                }
            elif isinstance(value, HashUpdate):
                self.redirect = {
                    "hash": value.hash,
                }
            elif isinstance(value, LocationUpdate):
                self.redirect = {
                    "url": value.redirect.url,
                    "refresh": True,
                    "title": value.title,
                }
            elif isinstance(value, PollUpdate):
                self.poll = value.to_json()

            if self.redirect:
                self._value = self.redirect

    def get_data(self):
        try:
            serialized_value = loads(dumps(self.value))
            serialized_args = loads(dumps(self.args))
            serialized_kwargs = loads(dumps(self.kwargs))

            return {
                "method": self.method_name,
                "args": serialized_args,
                "kwargs": serialized_kwargs,
                "value": serialized_value,
            }
        except Exception as e:
            logger.exception(e)

        return {}
