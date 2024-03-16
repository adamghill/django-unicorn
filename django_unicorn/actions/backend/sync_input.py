from django_unicorn.actions.base import Action, ActionResult
from django_unicorn.components import Component


class SyncInput(Action):

    action_type = "syncInput"

    def apply(
        self,
        component: Component,
        request, # : ComponentRequest,
    ) -> ActionResult:
        raise NotImplementedError()
