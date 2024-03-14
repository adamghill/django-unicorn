from django_unicorn.components import Component
from django_unicorn.actions.base import Action, ActionResult

class Reset(Action):
    
    action_type = "callMethod"
    method_name = "$reset"
    
    def apply(self, component: Component) -> ActionResult:
        raise NotImplementedError()
