
from django_unicorn.actions.frontend import FrontendAction
from django_unicorn.components import Component

from .base import BackendAction


class Validate(BackendAction):

    action_type = "callMethod"
    method_name = "$validate"

    def apply(
        self,
        component: Component,
        request, # : ComponentRequest,
    ) -> tuple[Component, FrontendAction]:
        # !!! This duplicates work done in ComponentResponse.from_context
        component.validate()
        return component, None
