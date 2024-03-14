from django_unicorn.components import Component
from django_unicorn.actions.base import Action, ActionResult

class Validate(Action):
    
    action_type = "callMethod"
    method_name = "$validate"
    
    def apply(self, component: Component) -> ActionResult:
        raise NotImplementedError()
