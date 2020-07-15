import hmac

from django.conf import settings
from django.http import JsonResponse

import orjson

from .components import get_component_class


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
    Component = get_component_class(component_name)
    component = Component(unicorn_id)

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

            if hasattr(component, name):
                setattr(component, name, value)

            data[name] = value

    rendered_component = component.render(component_name, include_component_init=False)

    res = {
        "id": unicorn_id,
        "dom": rendered_component,
        "data": data,
    }

    return JsonResponse(res)
