
from django_unicorn.actions.frontend import FrontendAction
from django_unicorn.components import Component

from .base import BackendAction


class Reset(BackendAction):

    action_type = "callMethod"
    method_name = "$reset"

    def apply(
        self,
        component: Component,
        request, # : ComponentRequest,
    ) -> tuple[Component, FrontendAction]:

        # create a clean object
        updated_component = Component.create(
            # we keep the original component's id and name
            component_id=component.component_id,
            component_name=component.component_name,
            request=request.request,
            use_cache=False,
        )

        #  Explicitly remove all errors and prevent validation from firing before render()
        updated_component.errors = {}

        # no FrontendAction needed
        return updated_component, None
