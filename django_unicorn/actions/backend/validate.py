
from django_unicorn.actions.frontend import FrontendAction
from django_unicorn.components import Component

from .base import BackendAction


class Validate(BackendAction):

    action_type = "callMethod"
    method_name = "$validate"

    def apply(self, component: Component) -> tuple[Component, FrontendAction]:
        raise NotImplementedError()
        # Handle the validate special action
        validate_all_fields = True

        # !!! where is this actually done...?
