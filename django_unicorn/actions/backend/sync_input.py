
from django_unicorn.actions.backend.utils import set_property_value
from django_unicorn.actions.frontend import FrontendAction
from django_unicorn.components import Component

from .base import BackendAction


class SyncInput(BackendAction):

    action_type = "syncInput"

    def apply(
        self,
        component: Component,
        request, # : ComponentRequest,
    ) -> tuple[Component, FrontendAction]:

        property_name = self.payload["name"]
        property_value = self.payload["value"]
        set_property_value(
            component,
            property_name,
            property_value,
        )

        # no FrontendAction needed
        return component, None
