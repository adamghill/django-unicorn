from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

from django_unicorn.actions.frontend import FrontendAction
from django_unicorn.call_method_parser import parse_call_method_name
from django_unicorn.components import Component

from .base import BackendAction

MIN_VALIDATION_ERROR_ARGS = 2

class CallMethod(BackendAction):

    action_type = "callMethod"

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
        from django_unicorn.actions.backend import (
            Refresh,
            Reset,
            SetAttribute,
            Toggle,
            Validate,
        )

        # This is the same as 'method_str' property above - but we don't have
        # an obj yet.
        method_str = data["payload"]["name"]

        # Note: all cases return a different Action subclass
        # if "=" in method_name: --> kwargs give with method
        #     return SetAttr.from_dict(data)
        if method_str == "$reset":
            return Reset.from_dict(data)
        elif method_str == "$refresh":
            return Refresh.from_dict(data)
        elif method_str == "$toggle":
            return Toggle.from_dict(data)
        elif method_str == "$validate":
            return Validate.from_dict(data)
        elif "=" in method_str and "(" not in method_str:
            # e.g. 'some_attribute=123'
            # but NOT something like 'some_method(key=123)'
            return SetAttribute.from_dict(data)
        else:
            # then we indeed have a CallMethod action and can use the normal
            # from_dict method to init
            return super().from_dict(data)

    def apply(
        self,
        component: Component,
        request, # : ComponentRequest,
    ) -> tuple[Component, FrontendAction]:

        # local import to prevent circular dep
        from django_unicorn.actions.frontend import MethodResult

        # Get all information needed for us to apply the method
        component_with_method = self._get_component_with_method(component)
        method_name = self.method_name
        method_args = self.method_args
        method_kwargs = self.method_kwargs

        # Now apply the method.
        # We do this inside a try/except in case the method works but validation
        # fails for the component afterwards.
        try:
            # call pre-method hook
            component_with_method.calling(method_name, method_args)

            # call the method
            method_return_value = self._call_method_name(
                component_with_method,
                method_name,
                method_args,
                method_kwargs,
            )

            # call post-method hook
            component_with_method.called(method_name, method_args)

            # ------------- TODO: improve this section's refactor -------------
            # This should not be handled within callMethod but instead at a
            # higher level. Or maybe `set_metadata` only needs to be called
            # with CallMethod actions...?

            # if its not already a subclass object, then we wrap it in a MethodResult,
            # which also subclasses FrontendAction
            if not isinstance(method_return_value, FrontendAction):
                method_return_value = MethodResult(value=method_return_value)

            # Unicorn frontend needs to know where this FrontendAction came from
            method_return_value.set_metadata(
                method_name,
                method_args,
                method_kwargs,
            )
            # -----------------------------------------------------------------

            return component, method_return_value

        except ValidationError as e:
            self._apply_validation_error(component, e)

            # no FrontendAction needed
            return component, None

    @property
    def method_str(self):
        return self.payload["name"]

    # OPTIMIZE: consider caching because it's used repeatedly
    # Alternatively, just build this during init
    @property
    def method_config(self):

        # The "replace" handles the special case where
        # "$parent.some_method" is given in the method_str, which we ignore for
        # now (it is handled in _get_component_with_method)
        method_str = self.method_str.replace("$parent.", "")

        # returns a tuple of (method_name, args, kwargs)
        # !!! This is the only place this util is used... Consider refactor
        # and pulling it in here.
        return parse_call_method_name(method_str)

    def _get_component_with_method(self, component):

        if "$parent" in self.method_str:
            return component

        else:
            parent_component = component.parent
            if not parent_component:
                raise Exception(
                    "$parent was requested but Component does not have a parent set"
                )
            parent_component.force_render = True
            return parent_component

    @property
    def method_name(self):
        return self.method_config[0]

    @property
    def method_args(self):
        return self.method_config[1]

    @property
    def method_kwargs(self):
        return self.method_config[2]

    @staticmethod
    def _apply_validation_error(self, component, e):
        if len(enumerate().args) < MIN_VALIDATION_ERROR_ARGS or not e.args[1]:
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

    # TODO: refactor and consider moving to a method of Component
    @staticmethod
    def _call_method_name(
            component: Component,
            method_name: str,
            args: tuple[any],
            kwargs: dict[str, any],
        ) -> any:
        """
        Calls the method name with parameters.

        Args:
            param component: Component to call method on.
            param method_name: Method name to call.
            param args: Tuple of arguments for the method.
            param kwargs: Dictionary of kwargs for the method.
        """

        if method_name is not None and hasattr(component, method_name):
            func = getattr(component, method_name)

            parsed_args = []
            parsed_kwargs = {}
            arguments = get_method_arguments(func)
            type_hints = get_type_hints(func)

            for argument in arguments:
                if argument in type_hints:
                    type_hint = type_hints[argument]

                    # Check that the type hint is a regular class or Union
                    # (which will also include Optional)
                    # TODO: Use types.UnionType to handle `|` for newer unions
                    if not isinstance(type_hint, type) and get_origin(type_hint) is not Union:
                        continue

                    is_model = False

                    try:
                        is_model = issubclass(type_hint, Model)
                    except TypeError:
                        pass

                    if is_model:
                        DbModel = type_hint
                        key = "pk"
                        value = None

                        if not kwargs:
                            value = args[len(parsed_args)]
                            parsed_args.append(DbModel.objects.get(**{key: value}))
                        else:
                            value = kwargs.get("pk")
                            parsed_kwargs[argument] = DbModel.objects.get(**{key: value})

                    elif argument in kwargs:
                        parsed_kwargs[argument] = cast_value(type_hint, kwargs[argument])
                    elif len(args) > len(parsed_args):
                        parsed_args.append(cast_value(type_hint, args[len(parsed_args)]))
                elif argument in kwargs:
                    parsed_kwargs[argument] = kwargs[argument]
                else:
                    parsed_args.append(args[len(parsed_args)])

            if parsed_args:
                return func(*parsed_args, **parsed_kwargs)
            elif parsed_kwargs:
                return func(**parsed_kwargs)
            else:
                return func()
