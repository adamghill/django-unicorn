from django_unicorn.components import Component
from django_unicorn.views.actions.base import Action, ActionResult

class Reset(Action):
    
    action_type = "callMethod"
    method_name = "$toggle"
    
    def apply(self, component: Component) -> ActionResult:
        raise NotImplementedError()
