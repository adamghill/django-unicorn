import hmac
from functools import wraps
from typing import Any, Dict, List, Tuple

import orjson
import shortuuid
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .components import UnicornView


class UnicornViewError(Exception):
    pass


def handle_error(view_func):
    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except UnicornViewError as e:
            return JsonResponse({"error": str(e)})
        except AssertionError as e:
            return JsonResponse({"error": str(e)})

    return wraps(view_func)(wrapped_view)


def _set_attribute(component: UnicornView, payload: Dict, data: Dict) -> None:
    """
    Sets properties on the component based on the payload.
    Also updates the data dictionary which gets set back as part of the payload.

    Args:
        param component: Component to set attributes on.
        param payload: Dictionary that comes with request.
        param data: Dictionary that gets sent back with the response.
    """

    attribute_name = payload.get("name")
    attribute_value = payload.get("value")

    if (
        attribute_name is not None
        and attribute_value is not None
        and hasattr(component, attribute_name)
    ):
        setattr(component, attribute_name, attribute_value)

    data[attribute_name] = attribute_value


def _parse_call_method_name(call_method_name: str) -> Tuple[str, List[Any]]:
    """
    Parses the method name from the request payload into a set of parameters to pass to a method.

    Args:
        param call_method_name: String representation of a method name with parameters, e.g. "set_name('Bob')"

    Returns:
        Tuple of method_name and a list of arguments.
    """

    method_name = call_method_name
    params: List[Any] = []

    if "(" in call_method_name and call_method_name.endswith(")"):
        param_idx = call_method_name.index("(")
        params_str = call_method_name[param_idx:]

        # Remove the arguments from the method name
        method_name = call_method_name.replace(params_str, "")

        # Remove parenthesis
        params_str = params_str[1:-1]

        if params_str == "":
            return (method_name, params)

        # Split up mutiple args
        params = params_str.split(",")

        for idx, arg in enumerate(params):
            params[idx] = _handle_arg(arg)

        # TODO: Handle kwargs

    return (method_name, params)


def _handle_arg(arg):
    """
    Clean up arguments. Mostly used to handle strings.

    Returns:
        Cleaned up argument.
    """
    if (arg.startswith("'") and arg.endswith("'")) or (
        arg.startswith('"') and arg.endswith('"')
    ):
        return arg[1:-1]


def _call_method_name(
    component: UnicornView, method_name: str, params: List[Any], data: Dict
) -> None:
    """
    Calls the method name with parameters.
    Also updates the data dictionary which gets set back as part of the payload.

    Args:
        param component: Component to call method on.
        param method_name: Method name to call.
        param params: List of arguments for the method.
        param data: Dictionary that gets sent back with the response.
    """

    if method_name is not None and hasattr(component, method_name):
        func = getattr(component, method_name)

        if params:
            func(*params)
        else:
            func()

        # Re-set all attributes because they could have changed after the method call
        for (attribute_name, attribute_value,) in component._attributes().items():
            data[attribute_name] = attribute_value


class ComponentRequest:
    """
    Parses, validates, and stores all of the data from the message request.
    """

    def __init__(self, request):
        self.body = {}

        try:
            self.body = orjson.loads(request.body)
            assert self.body, "Invalid JSON body"
        except orjson.JSONDecodeError as e:
            raise UnicornViewError("Body could not be parsed") from e

        self.data = self.body.get("data")
        assert self.data is not None, "Missing data"  # data could theoretically be {}

        self.id = self.body.get("id")
        assert self.id, "Missing component id"

        self.validate_checksum()

        self.action_queue = self.body.get("actionQueue", [])

    def validate_checksum(self):
        """
        Validates that the checksum in the request matches the data.

        Returns:
            Raises `AssertionError` if the checksums don't match.
        """
        checksum = self.body.get("checksum")
        assert checksum, "Missing checksum"

        generated_checksum = hmac.new(
            str.encode(settings.SECRET_KEY),
            orjson.dumps(self.data),
            digestmod="sha256",
        ).hexdigest()
        generated_checksum = shortuuid.uuid(generated_checksum)[:8]
        assert checksum == generated_checksum, "Checksum does not match"


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
        JSON with the following structure:
        {
            "id": component_id,
            "dom": html,  // re-rendered version of the component after actions in the payload are completed
            "data": {},  // updated data after actions in the payload are completed
        }
    """

    assert component_name, "Missing component name in url"

    component_request = ComponentRequest(request)
    data = component_request.data

    component = UnicornView.create(
        component_id=component_request.id, component_name=component_name
    )

    for (name, value) in data.items():
        if hasattr(component, name):
            setattr(component, name, value)

    for action in component_request.action_queue:
        action_type = action.get("type")
        payload = action.get("payload", {})

        if action_type == "syncInput":
            _set_attribute(component, payload, component_request.data)
        elif action_type == "callMethod":
            call_method_name = payload.get("name", "")
            assert call_method_name, "Missing 'name' key for callMethod"

            # Handle the special case of the reset action
            if call_method_name == "reset" or call_method_name == "reset()":
                component = UnicornView.create(
                    component_id=component_request.id,
                    component_name=component_name,
                    skip_cache=True,
                )
                # Reset the data based on component's attributes
                data = component._attributes()
            elif "=" in call_method_name:
                call_method_name_split = call_method_name.split("=")
                property_name = call_method_name_split[0]
                property_value = _handle_arg(call_method_name_split[1])

                if hasattr(component, property_name):
                    setattr(component, property_name, property_value)
                    data[property_name] = property_value
            else:
                (method_name, params) = _parse_call_method_name(call_method_name)
                _call_method_name(component, method_name, params, data)
        else:
            raise UnicornViewError(f"Unknown action_type '{action_type}'")

    rendered_component = component.render()

    res = {
        "id": component_request.id,
        "dom": rendered_component,
        "data": data,
    }

    return JsonResponse(res)
