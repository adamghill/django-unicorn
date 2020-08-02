import hmac
from typing import Any, Dict, List, Tuple

import orjson
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .components import UnicornView


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
            # Remove extra quotes for strings
            if (arg.startswith("'") and arg.endswith("'")) or (
                arg.startswith('"') and arg.endswith('"')
            ):
                params[idx] = arg[1:-1]

        # TODO: Handle kwargs

    return (method_name, params)


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


@csrf_protect
@require_POST
def message(request: HttpRequest, component_name: str) -> JsonResponse:
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

    if not component_name:
        return JsonResponse({"error": "Missing component name in url"})

    body = {}

    try:
        body = orjson.loads(request.body)
    except orjson.JSONDecodeError:
        return JsonResponse({"error": "Body could not be parsed"})

    if not body:
        return JsonResponse({"error": "Invalid JSON body"})

    data = body.get("data", {})

    if not data:
        return JsonResponse({"error": "Missing data"})

    checksum = body.get("checksum", "")

    if not checksum:
        return JsonResponse({"error": "Missing checksum"})

    generated_checksum = hmac.new(
        str.encode(settings.SECRET_KEY), orjson.dumps(data), digestmod="sha256",
    ).hexdigest()

    if checksum != generated_checksum:
        return JsonResponse({"error": "Checksum does not match"})

    component_id = body.get("id")

    if not component_id:
        return JsonResponse({"error": "Missing component id"})

    component = UnicornView.create(
        component_id=component_id, component_name=component_name
    )

    for (name, value) in data.items():
        if hasattr(component, name):
            setattr(component, name, value)

    action_queue = body.get("actionQueue", [])

    for action in action_queue:
        action_type = action.get("type")
        payload = action.get("payload", {})

        if action_type == "syncInput":
            _set_attribute(component, payload, data)
        elif action_type == "callMethod":
            call_method_name = payload.get("name", "")

            if not call_method_name:
                return JsonResponse({"error": "Missing 'name' key for callMethod"})

            # Handle the special case of the reset action
            if call_method_name == "reset" or call_method_name == "reset()":
                component = UnicornView.create(
                    component_id=component_id,
                    component_name=component_name,
                    skip_cache=True,
                )
                # Reset the data based on component's attributes
                data = component._attributes()

                break

            (method_name, params) = _parse_call_method_name(call_method_name)
            _call_method_name(component, method_name, params, data)
        else:
            return JsonResponse({"error": f"Unknown action_type '{action_type}'"})

    rendered_component = component.render()

    res = {
        "id": component_id,
        "dom": rendered_component,
        "data": data,
    }

    return JsonResponse(res)
