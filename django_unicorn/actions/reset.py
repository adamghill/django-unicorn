from django_unicorn.components import Component
from django_unicorn.actions.base import Action, ActionResult

class Reset(Action):
    
    action_type = "callMethod"
    method_name = "$reset"
    
    def apply(
        self, 
        component: Component, 
        request, # : ComponentRequest,
    ) -> ActionResult:
        
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
        
        return updated_component
