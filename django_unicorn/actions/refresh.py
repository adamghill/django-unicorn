from django_unicorn.components import Component
from django_unicorn.actions.base import Action, ActionResult

class Refresh(Action):
    
    action_type = "callMethod"
    method_name = "$refresh"
    
    def apply(self, component: Component) -> ActionResult:
        raise NotImplementedError()
