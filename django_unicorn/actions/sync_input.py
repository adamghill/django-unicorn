from django_unicorn.components import Component
from django_unicorn.views.actions.base import Action, ActionResult

class SyncInput(Action):
    
    action_type = "syncInput"
    
    def apply(self, component: Component) -> ActionResult:
        raise NotImplementedError()
