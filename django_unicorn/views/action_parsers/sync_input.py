from typing import Dict

from django_unicorn.components import UnicornView
from django_unicorn.views.objects import ComponentRequest

from .utils import set_property_value


def handle(component_request: ComponentRequest, component: UnicornView, payload: Dict):
    property_name = payload.get("name")
    property_value = payload.get("value")
    set_property_value(component, property_name, property_value, component_request.data)
