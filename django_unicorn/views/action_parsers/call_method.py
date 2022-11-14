from typing import Any, Dict, Tuple

from django.db.models import Model

from django_unicorn.call_method_parser import (
    InvalidKwarg,
    parse_call_method_name,
    parse_kwarg,
)
from django_unicorn.components import UnicornView
from django_unicorn.decorators import timed
from django_unicorn.utils import get_method_arguments, get_type_hints
from django_unicorn.views.action_parsers.utils import set_property_value
from django_unicorn.views.objects import ComponentRequest, Return
from django_unicorn.views.utils import set_property_from_data


def handle(component_request: ComponentRequest, component: UnicornView, payload: Dict):
    call_method_name = payload.get("name", "")
    assert call_method_name, "Missing 'name' key for callMethod"

    (method_name, args, kwargs) = parse_call_method_name(call_method_name)
    return_data = Return(method_name, args, kwargs)
    setter_method = {}

    is_refresh_called = False
    is_reset_called = False
    validate_all_fields = False

    if "=" in call_method_name:
        try:
            setter_method = parse_kwarg(call_method_name, raise_if_unparseable=True)
        except InvalidKwarg:
            pass

    if setter_method:
        property_name = list(setter_method.keys())[0]
        property_value = setter_method[property_name]

        set_property_value(component, property_name, property_value)
        return_data = Return(property_name, [property_value])
    else:
        if method_name == "$refresh":
            # Handle the refresh special action
            component = UnicornView.create(
                component_id=component_request.id,
                component_name=component_request.name,
                request=component_request.request,
            )

            # Set component properties based on request data
            for (
                property_name,
                property_value,
            ) in component_request.data.items():
                set_property_from_data(component, property_name, property_value)
            component.hydrate()

            is_refresh_called = True
        elif method_name == "$reset":
            # Handle the reset special action
            component = UnicornView.create(
                component_id=component_request.id,
                component_name=component_request.name,
                request=component_request.request,
                use_cache=False,
            )

            #  Explicitly remove all errors and prevent validation from firing before render()
            component.errors = {}
            is_reset_called = True
        elif method_name == "$toggle":
            for property_name in args:
                property_value = _get_property_value(component, property_name)
                property_value = not property_value

                set_property_value(component, property_name, property_value)
        elif method_name == "$validate":
            # Handle the validate special action
            validate_all_fields = True
        else:
            component.calling(method_name, args)
            return_data.value = _call_method_name(component, method_name, args, kwargs)
            component.called(method_name, args)

    return (
        component,
        is_refresh_called,
        is_reset_called,
        validate_all_fields,
        return_data,
    )


@timed
def _call_method_name(
    component: UnicornView, method_name: str, args: Tuple[Any], kwargs: Dict[str, Any]
) -> Any:
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

        if len(args) == 1 or len(kwargs) == 1:
            arguments = get_method_arguments(func)
            type_hints = get_type_hints(func)

            for argument in arguments:
                if argument in type_hints:
                    type_hint = type_hints[argument]

                    if isinstance(type_hint, type) and issubclass(type_hint, Model):
                        DbModel = type_hint
                        key = "pk"
                        value = None

                        if args:
                            value = args[0]
                        elif kwargs:
                            kwargs = kwargs.copy()  # no mutation of original
                            (key, value) = list(kwargs.items())[0]
                            del kwargs[key]

                        model = DbModel.objects.get(**{key: value})
                        args = [model]

        if args and kwargs:
            return func(*args, **kwargs)
        elif args:
            return func(*args, **kwargs)
        elif kwargs:
            return func(**kwargs)
        else:
            return func()


@timed
def _get_property_value(component: UnicornView, property_name: str) -> Any:
    """
    Gets property value from the component based on the property name.
    Handles nested property names.

    Args:
        param component: Component to get property values from.
        param property_name: Property name. Can be "dot-notation" to get nested properties.
    """

    assert property_name is not None, "property_name name is required"

    # Handles nested properties
    property_name_parts = property_name.split(".")
    component_or_field = component

    for (idx, property_name_part) in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                return getattr(component_or_field, property_name_part)
            else:
                component_or_field = getattr(component_or_field, property_name_part)
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                return component_or_field[property_name_part]
            else:
                component_or_field = component_or_field[property_name_part]
