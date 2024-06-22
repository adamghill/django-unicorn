from typing import Dict

from django_unicorn.components import UnicornView
from django_unicorn.views.action_parsers.utils import set_property_value
from django_unicorn.views.objects import ComponentRequest


def handle(component_request: ComponentRequest, component: UnicornView, payload: Dict):
    property_name = payload.get("name")
    property_value = payload.get("value")

    call_updated_method = True

    # If there is more than one action then only call the updated methods for the last action in the queue
    if len(component_request.action_queue) > 1:
        call_updated_method = False
        last_action = component_request.action_queue[-1:][0]

        if last_action.payload.get("name") == property_name and last_action.payload.get("value") == property_value:
            call_updated_method = True

    set_property_value(
        component, property_name, property_value, component_request.data, call_updated_method=call_updated_method
    )
