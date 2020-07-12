from django.http import JsonResponse

import orjson

from .components import get_component_class


def message(request, component_name):
    body = orjson.loads(request.body)

    unicorn_id = body.get("id")
    Component = get_component_class(component_name)
    component = Component(unicorn_id)

    data = body.get("data", {})

    for (name, value) in data.items():
        if hasattr(component, name):
            setattr(component, name, value)

    rendered_component = component.render(component_name)

    res = {
        "id": unicorn_id,
        "dom": rendered_component,
    }

    return JsonResponse(res)
