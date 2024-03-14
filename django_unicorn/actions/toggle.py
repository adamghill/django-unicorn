from django_unicorn.components import Component
from django_unicorn.actions.base import Action, ActionResult

class Toggle(Action):
    
    action_type = "callMethod"
    method_name = "$toggle"
    
    def apply(self, component: Component) -> ActionResult:
        raise NotImplementedError()
