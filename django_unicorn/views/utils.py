import logging
from dataclasses import is_dataclass
from typing import Any, Dict, Union

from django.db.models import Model, QuerySet

from django_unicorn.components import UnicornField, UnicornView
from django_unicorn.components.typing import QuerySetType
from django_unicorn.decorators import timed
from django_unicorn.utils import get_type_hints


try:
    from typing import get_args, get_origin
except ImportError:
    # Fallback to dunder methods for older versions of Python
    def get_args(type_hint):
        if hasattr(type_hint, "__args__"):
            return type_hint.__args__

    def get_origin(type_hint):
        if hasattr(type_hint, "__origin__"):
            return type_hint.__origin__


logger = logging.getLogger(__name__)


@timed
def set_property_from_data(
    component_or_field: Union[UnicornView, UnicornField, Model],
    name: str,
    value: Any,
) -> None:
    """
    Sets properties on the component based on passed-in data.
    """

    try:
        if not hasattr(component_or_field, name):
            return
    except ValueError:
        # Treat ValueError the same as a missing field because trying to access a many-to-many
        # field before the model's pk will throw this exception
        return

    field = getattr(component_or_field, name)
    component_field_is_model_or_unicorn_field = (
        _is_component_field_model_or_unicorn_field(component_or_field, name)
    )

    # UnicornField and Models are always a dictionary (can be nested)
    if component_field_is_model_or_unicorn_field:
        # Re-get the field since it might have been set in `_is_component_field_model_or_unicorn_field`
        field = getattr(component_or_field, name)

        type_hints = get_type_hints(component_or_field)

        if isinstance(value, dict):
            for key in value.keys():
                key_value = value[key]
                set_property_from_data(field, key, key_value)
    elif hasattr(field, "related_val"):
        # Use `related_val` to check for many-to-many
        field.set(value)
    else:
        type_hints = get_type_hints(component_or_field)
        type_hint = type_hints.get(name)

        if _is_queryset(field, type_hint, value):
            value = _create_queryset(field, type_hint, value)
        elif type_hint:
            if is_dataclass(type_hint):
                value = type_hint(**value)
            else:
                # Construct the specified type by passing the value in
                # Usually the value will be a string (because it is coming from JSON)
                # and basic types can be constructed by passing in a string,
                # i.e. int("1") or float("1.1")
                try:
                    value = type_hint(value)
                except TypeError:
                    # Ignore this exception because some type-hints can't be instantiated like this (e.g. `List[]`)
                    pass

        if hasattr(component_or_field, "_set_property"):
            # Can assume that `component_or_field` is a component
            component_or_field._set_property(
                name, value, call_updating_method=True, call_updated_method=False
            )
        else:
            setattr(component_or_field, name, value)


@timed
def _is_component_field_model_or_unicorn_field(
    component_or_field: Union[UnicornView, UnicornField, Model],
    name: str,
) -> bool:
    """
    Determines whether a component's field is a Django `Model` or `UnicornField` either
    by checking the field's instance or inspecting the type hints.

    One side-effect is that the field will be instantiated if it is currently `None` and
    the type hint is available.

    Args:
        component: `UnicornView` to check.
        name: Name of the field.

    Returns:
        Whether the field is a Django `Model` or `UnicornField`.
    """
    field = getattr(component_or_field, name)

    if isinstance(field, UnicornField) or isinstance(field, Model):
        return True

    is_subclass_of_model = False
    is_subclass_of_unicorn_field = False
    component_type_hints = {}

    try:
        component_type_hints = get_type_hints(component_or_field)

        if name in component_type_hints:
            is_subclass_of_model = issubclass(component_type_hints[name], Model)

            if not is_subclass_of_model:
                is_subclass_of_unicorn_field = issubclass(
                    component_type_hints[name], UnicornField
                )

            # Construct a new class if the field is None and there is a type hint available
            if field is None:
                if is_subclass_of_model or is_subclass_of_unicorn_field:
                    field = component_type_hints[name]()
                    setattr(component_or_field, name, field)
    except TypeError:
        pass

    return is_subclass_of_model or is_subclass_of_unicorn_field


def _is_queryset(field, type_hint, value):
    """
    Determines whether a field is a `QuerySet` or not based on the current instance of the
    component or the type hint.
    """

    return (
        isinstance(field, QuerySet)
        or (type_hint and get_origin(type_hint) is QuerySetType)
    ) and isinstance(value, list)


def _create_queryset(field, type_hint, value) -> QuerySet:
    """
    Create a queryset based on the `value`. If needed, the queryset will be created based on the `QuerySetType`.

    For example, all of these ways fields are equivalent:

    ```
    class TestComponent(UnicornView):
        queryset_with_empty_list: QuerySetType[SomeModel] = []
        queryset_with_none: QuerySetType[SomeModel] = None
        queryset_with_empty_queryset: QuerySetType[SomeModel] = SomeModel.objects.none()
        queryset_with_no_typehint = SomeModel.objects.none()
    ```

    Params:
        field: Field of the component.
        type_hint: The optional type hint for the field.
        value: JSON.
    """

    # Get original queryset, update it with dictionary data and then
    # re-set the queryset; this is required because otherwise the
    # property changes type from a queryset to the serialized queryset
    # (which is an array of dictionaries)
    queryset = field
    model_type = None

    if type_hint and not isinstance(queryset, QuerySet):
        type_arguments = get_args(type_hint)

        if type_arguments:
            # First type argument should be the type of the model
            queryset = type_arguments[0].objects.none()
            model_type = type_arguments[0]

    if not model_type and not isinstance(queryset, QuerySet):
        raise Exception(f"Getting Django Model type failed for type: {type(queryset)}")

    if not model_type:
        # Assume that `queryset` is _actually_ a QuerySet so grab the
        # `model` attribute in that case
        model_type = queryset.model

    for model_value in value:
        model_found = False

        # The following portion uses the internal `_result_cache` QuerySet API which
        # is private and could potentially change in the future, but not sure how
        # else to change internal models or append a new model to a QuerySet (probably
        # because it isn't really allowed)
        if queryset._result_cache is None:
            # Explicitly set `_result_cache` to an empty list
            queryset._result_cache = []

        for (idx, model) in enumerate(queryset._result_cache):
            if hasattr(model, "pk") and model.pk == model_value.get("pk"):
                constructed_model = _construct_model(model_type, model_value)
                queryset._result_cache[idx] = constructed_model
                model_found = True

        if not model_found:
            constructed_model = _construct_model(model_type, model_value)
            queryset._result_cache.append(constructed_model)

    return queryset


def _construct_model(model_type, model_data: Dict):
    """
    Construct a model based on the type and dictionary data.
    """

    if not model_data:
        return None

    model = model_type()

    for field_name in model_data.keys():
        for field in model._meta.fields:
            if field.name == field_name or (field_name == "pk" and field.primary_key):
                column_name = field.name

                if field.is_relation:
                    column_name = field.attname

                setattr(model, column_name, model_data[field_name])

                break

    return model
