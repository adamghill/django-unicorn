import hmac

from django.conf import settings
from django.http import JsonResponse

import orjson

from .components import Component


def message(request, component_name):
    body = orjson.loads(request.body)
    data = body.get("data", {})
    checksum = body.get("checksum")

    generated_checksum = hmac.new(
        str.encode(settings.SECRET_KEY), orjson.dumps(data), digestmod="sha256",
    ).hexdigest()

    if checksum != generated_checksum:
        return JsonResponse({"error": "Checksum does not match"})

    unicorn_id = body.get("id")
    component = Component.create(component_name, id=unicorn_id)

    for (name, value) in data.items():
        if hasattr(component, name):
            setattr(component, name, value)

    action_queue = body.get("actionQueue", [])

    for action in action_queue:
        action_type = action.get("type")
        payload = action.get("payload", {})

        if action_type == "syncInput":
            name = payload.get("name")
            value = payload.get("value")

            if name is not None and value is not None and hasattr(component, name):
                setattr(component, name, value)

            data[name] = value
        elif action_type == "callMethod":
            name = payload.get("name")
            params = []

            if "(" in name and ")" in name:
                param_idx = name.index("(")
                params = name[param_idx:]

                # Remove the arguments from the method name used later
                name = name.replace(params, "")

                # Remove paranthesis
                params = params[1:-1]

                # Rmeove extra quotes for strings
                if params.startswith("'") and params.endswith("'"):
                    params = params[1:-1]
                elif params.startswith('"') and params.endswith('"'):
                    params = params[1:-1]

                # TODO: Handle kwargs
                params = params.split(",")

            if name is not None and hasattr(component, name):
                func = getattr(component, name)

                if params:
                    func(*params)
                else:
                    func()

                for (
                    attribute_name,
                    attribute_value,
                ) in component.__attributes__().items():
                    data[attribute_name] = attribute_value

    rendered_component = component.render(include_component_init=False)

    res = {
        "id": unicorn_id,
        "dom": rendered_component,
        "data": data,
    }

    return JsonResponse(res)
