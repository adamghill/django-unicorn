from django_unicorn.components import Component
from django_unicorn.actions.base import Action, ActionResult

MIN_VALIDATION_ERROR_ARGS = 2

class CallMethod(Action):
    
    action_type = "callMethod"
    
    def __init__(self, payload: dict, partials: list):
        super().__init__(payload, partials)
        
        # This is often updated in subclasses
    
    @property
    def method_name(self):
        return self.payload["name"]
    
    def apply(self, component: Component) -> ActionResult:
        raise NotImplementedError()
        try:
            # TODO: continue refactor of this method
            (
                component,
                return_data,
            ) = call_method.handle(self, component, action.payload)
            self.action_results.append(return_data)
        except ValidationError as e:
            if len(e.args) < MIN_VALIDATION_ERROR_ARGS or not e.args[1]:
                raise AssertionError("Error code must be specified") from e

            if hasattr(e, "error_list"):
                error_code = e.args[1]

                for error in e.error_list:
                    if NON_FIELD_ERRORS in component.errors:
                        component.errors[NON_FIELD_ERRORS].append(
                            {"code": error_code, "message": error.message}
                        )
                    else:
                        component.errors[NON_FIELD_ERRORS] = [
                            {"code": error_code, "message": error.message}
                        ]
            elif hasattr(e, "message_dict"):
                for field, message in e.message_dict.items():
                    if not e.args[1]:
                        raise AssertionError(
                            "Error code must be specified"
                        ) from e

                    error_code = e.args[1]

                    if field in component.errors:
                        component.errors[field].append(
                            {"code": error_code, "message": message}
                        )
                    else:
                        component.errors[field] = [
                            {"code": error_code, "message": message}
                        ]

    @classmethod
    def from_dict(cls, data: dict):
        
        # Ideally, we could utilize the `Action.get_action_type_mappings` to
        # determine all Action types. However, callMethod can lead to various 
        # subclasses like Refresh/Reset/Toggle.
        # It'd be nice if these subclasses return a different action_type from
        # the frontend but I'm not sure if that's easily achieved.
        # If that's ever added, then this from_dict method can be removed.
        # For now we need to create a CallMethod class and inspect it to
        # decide whether to "punt" it to another Action type.
        
        # local import to prevent circular deps
        from django_unicorn.actions import (
            Refresh,
            Reset,
            Toggle,
            Validate,
        )

        payload_name = data["payload"]["name"]
        
        # Note: all cases return a different Action subclass
        # if "=" in method_name: --> kwargs give with method
        #     return SetAttr.from_dict(data)
        if payload_name == "$reset":
            return Reset.from_dict(data)
        elif payload_name == "$refresh":
            return Refresh.from_dict(data)
        elif payload_name == "$toggle":
            return Toggle.from_dict(data)
        else:
            # then we indeed have a CallMethod action and can use the normal
            # from_dict method to init
            return super().from_dict(data)
