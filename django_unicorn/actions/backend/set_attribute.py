
from django_unicorn.actions.frontend import FrontendAction
from django_unicorn.components import Component

from .base import BackendAction
from .utils import set_property_value


class SetAttribute(BackendAction):

    action_type = "callMethod"
    method_name = "set_property"  # TODO: add as method to Component class

    def apply(
        self,
        component: Component,
        request, # : ComponentRequest,
    ) -> tuple[Component, FrontendAction]:

        # TODO: convert set_property_value to a Component method
        set_property_value(
            component,
            self.attribute_to_set,
            self.new_attribute_value,
        )

        # TODO: build FrontendAction for this
        # return_data = Return(property_name, [property_value])

        return component, None

    @property
    def attribute_to_set(self):
        return self.attribute_config[0]

    @property
    def new_attribute_value(self):
        return self.attribute_config[1]

    # OPTIMIZE: consider caching because it's used repeatedly
    # Alternatively, just build this during init
    @property
    def attribute_config(self):
        # TODO: add support for '$parent.example=123'

        # it's under "name" because this normally is callMethod -> name of method
        input_str = self.payload["name"]

        if input_str.count("=") != 1:
            raise ValueError(
                "Improper SetAttribute config. Expected something like "
                f"'attribute=123' but recieved '{input_str}'"
            )

        attribute_name, new_value = self.payload["name"].split("=")

        return attribute_name, new_value
