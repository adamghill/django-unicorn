import hmac

from django.conf import settings
from django.http import JsonResponse

import orjson

from .components import UnicornView


def message(request, component_name):
    body = orjson.loads(request.body)
    data = body.get("data", {})
    checksum = body.get("checksum")

    generated_checksum = hmac.new(
        str.encode(settings.SECRET_KEY), orjson.dumps(data), digestmod="sha256",
    ).hexdigest()

    if checksum != generated_checksum:
        return JsonResponse({"error": "Checksum does not match"})

    component_id = body.get("id")
    view = UnicornView.create(component_id=component_id, component_name=component_name)

    for (name, value) in data.items():
        if hasattr(view, name):
            setattr(view, name, value)

    action_queue = body.get("actionQueue", [])

    for action in action_queue:
        action_type = action.get("type")
        payload = action.get("payload", {})

        if action_type == "syncInput":
            name = payload.get("name")
            value = payload.get("value")

            if name is not None and value is not None and hasattr(view, name):
                setattr(view, name, value)

            data[name] = value
        elif action_type == "callMethod":
            name = payload.get("name")
            params = []

            if "(" in name and ")" in name:
                param_idx = name.index("(")
                params = name[param_idx:]

                # Remove the arguments from the method name
                name = name.replace(params, "")

                # Remove paranthesis
                params = params[1:-1]

                # Remove extra quotes for strings
                if params.startswith("'") and params.endswith("'"):
                    params = params[1:-1]
                elif params.startswith('"') and params.endswith('"'):
                    params = params[1:-1]

                # TODO: Handle kwargs
                params = params.split(",")

            if name is not None and hasattr(view, name):
                func = getattr(view, name)

                if params:
                    func(*params)
                else:
                    func()

                for (attribute_name, attribute_value,) in view._attributes().items():
                    data[attribute_name] = attribute_value

    rendered_component = view.render()

    res = {
        "id": component_id,
        "dom": rendered_component,
        "data": data,
    }

    return JsonResponse(res)
