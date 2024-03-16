
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
        raise NotImplementedError()
