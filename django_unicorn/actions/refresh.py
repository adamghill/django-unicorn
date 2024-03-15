from django_unicorn.components import Component
from django_unicorn.actions.base import Action, ActionResult
from django_unicorn.views.utils import set_property_from_data


class Refresh(Action):
    
    action_type = "callMethod"
    method_name = "$refresh"
    
    def apply(
        self, 
        component: Component, 
        request, # : ComponentRequest,
    ) -> Component:
        
        # grab a clean object - can be from cache
        updated_component = Component.create(
            # we keep the original component's id and name
            component_id=component.component_id,
            component_name=component.component_name,
            request=request.request,
        )

        # Set component properties based on request data
        for property_name, property_value in request.data.items():
            set_property_from_data(updated_component, property_name, property_value)

        updated_component.hydrate()
        
        return updated_component
