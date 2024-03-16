
from django_unicorn.actions.frontend import FrontendAction
from django_unicorn.call_method_parser import parse_call_method_name
from django_unicorn.components import Component

from .base import BackendAction
from .utils import set_property_value


class Toggle(BackendAction):

    action_type = "callMethod"
    method_name = "$toggle"

    def apply(
        self,
        component: Component,
        request, # : ComponentRequest,
    ) -> tuple[Component, FrontendAction]:

        for property_name in self.properties_to_toggle:
            property_value = component._get_property(property_name)

            if not isinstance(property_value, bool):
                raise ValueError("You can only call '$toggle' on boolean attributes")

            # toggle/flip the boolean
            property_value = not property_value

            # !!! consider making this util a method of Component
            set_property_value(component, property_name, property_value)

        # no FrontendAction needed
        return component, None

    @property
    def properties_to_toggle(self):
        # !!! Code is pretty much copy/pasted from CallMethod's method_config
        # so I need to continue the refactor here.
        method_str = self.method_str.replace("$parent.", "")
        return parse_call_method_name(method_str)[1]  # 2nd element in tuple is "args"
