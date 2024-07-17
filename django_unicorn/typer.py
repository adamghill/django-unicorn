import logging
from dataclasses import is_dataclass
from datetime import date, datetime, time, timedelta, timezone
from inspect import signature
from typing import Any, Dict, List, Optional, Tuple, Union
from typing import get_type_hints as typing_get_type_hints
from uuid import UUID

try:
    from pydantic import BaseModel

    def _check_pydantic(cls) -> bool:
        return issubclass(cls, BaseModel)

except ImportError:

    def _check_pydantic(cls) -> bool:  # noqa: ARG001
        return False


from django.db.models import Model, QuerySet
from django.utils.dateparse import (
    parse_date,
    parse_datetime,
    parse_duration,
    parse_time,
)

from django_unicorn.typing import QuerySetType

try:
    from typing import get_args, get_origin
except ImportError:
    # Fallback to dunder methods for older versions of Python
    def get_args(tp: Any) -> Tuple[Any, ...]:
        if hasattr(tp, "__args__"):
            return tp.__args__
        return ()

    def get_origin(tp: Any) -> Optional[Any]:
        if hasattr(tp, "__origin__"):
            return tp.__origin__
        return None


try:
    from cachetools.lru import LRUCache
except ImportError:
    from cachetools import LRUCache


logger = logging.getLogger(__name__)

type_hints_cache = LRUCache(maxsize=100)
function_signature_cache = LRUCache(maxsize=100)


def _parse_bool(value):
    return str(value) == "True"


# Functions that attempt to convert something that failed while being parsed by
# `ast.literal_eval`.
CASTERS = {
    datetime: parse_datetime,
    time: parse_time,
    date: parse_date,
    timedelta: parse_duration,
    UUID: UUID,
    bool: _parse_bool,
}


def get_type_hints(obj) -> Dict:
    """Get type hints from an object. These get cached in a local memory cache for quicker look-up later.

    Returns:
        An empty dictionary if no type hints can be retrieved.
    """

    try:
        if obj in type_hints_cache:
            return type_hints_cache[obj]
    except TypeError:
        # Ignore issues with checking for an object in the cache, e.g. when a Django model is missing a PK
        pass

    try:
        type_hints = typing_get_type_hints(obj)

        # Cache the type hints just in case
        type_hints_cache[obj] = type_hints

        return type_hints
    except (TypeError, NameError):
        # Return an empty dictionary when there is a TypeError. From `get_type_hints`: "TypeError is
        # raised if the argument is not of a type that can contain annotations, and an empty dictionary
        # is returned if no annotations are present"
        return {}


def cast_value(type_hint, value):
    """Try to cast the value based on the type hint and
    `django_unicorn.call_method_parser.CASTERS`.

    Additional features:
    - convert `int`/`float` epoch to `datetime` or `date`
    - instantiate the `type_hint` class with passed-in value
    """

    type_hints = []

    if get_origin(type_hint) is Union or get_origin(type_hint) is list:
        for arg in get_args(type_hint):
            type_hints.append(arg)
    else:
        type_hints.append(type_hint)

    if get_origin(type_hint) is list:
        if len(type_hints) == 1:
            # There should only be one argument for a list type hint
            arg = type_hints[0]

            # Handle type hints that are a list by looping over the value and
            # casting each item individually
            return [cast_value(arg, item) for item in value]

    # Handle Optional type hint and the value is None
    if type(None) in type_hints and value is None:
        return value

    for _type_hint in type_hints:
        if _type_hint == type(None):  # noqa: E721
            continue

        caster = CASTERS.get(_type_hint)

        if caster:
            try:
                value = caster(value)
                break
            except TypeError:
                if (_type_hint is datetime or _type_hint is date) and (isinstance(value, (float, int))):
                    try:
                        value = datetime.fromtimestamp(value, tz=timezone.utc)

                        if _type_hint is date:
                            value = value.date()

                        break
                    except ValueError:
                        pass
        else:
            if issubclass(_type_hint, Model):
                continue

            if _check_pydantic(_type_hint) or is_dataclass(_type_hint):
                value = _type_hint(**value)
                break

            value = _type_hint(value)
            break

    return value


def cast_attribute_value(obj, name, value):
    """Try to cast the value of an object's attribute based on the type hint."""

    type_hints = get_type_hints(obj)
    type_hint = type_hints.get(name)

    if type_hint:
        if is_queryset(obj, type_hint, value):
            # Do not try to cast the queryset here
            pass
        elif not is_dataclass(type_hint):
            try:
                value = cast_value(type_hint, value)
            except TypeError:
                # Ignore this exception because some type-hints can't be instantiated like this (e.g. `List[]`)
                pass

    return value


def get_method_arguments(func) -> List[str]:
    """Gets the arguments for a method.

    Returns:
        A list of strings, one for each argument.
    """

    if func in function_signature_cache:
        return function_signature_cache[func]

    function_signature = signature(func)
    function_signature_cache[func] = list(function_signature.parameters)

    return function_signature_cache[func]


def is_queryset(obj, type_hint, value):
    """Determines whether an obj is a `QuerySet` or not based on the current instance of the
    component or the type hint."""

    return (
        (isinstance(obj, QuerySet) or (type_hint and get_origin(type_hint) is QuerySetType))
        and isinstance(value, list)
        or isinstance(value, QuerySet)
    )


def _construct_model(model_type, model_data: Dict):
    """Construct a model based on the type and dictionary data."""

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


def create_queryset(obj, type_hint, value) -> QuerySet:
    """Create a queryset based on the `value`. If needed, the queryset will be created based on the `QuerySetType`.

    For example, all of these ways fields are equivalent:

    class TestComponent(UnicornView):
        queryset_with_empty_list: QuerySetType[SomeModel] = []
        queryset_with_none: QuerySetType[SomeModel] = None
        queryset_with_empty_queryset: QuerySetType[SomeModel] = SomeModel.objects.none()
        queryset_with_no_typehint = SomeModel.objects.none()

    Params:
        obj: Object.
        type_hint: The optional type hint for the field.
        value: JSON.
    """

    # Get original queryset, update it with dictionary data and then
    # re-set the queryset; this is required because otherwise the
    # property changes type from a queryset to the serialized queryset
    # (which is an array of dictionaries)
    queryset = obj
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

        for idx, model in enumerate(queryset._result_cache):
            if hasattr(model, "pk") and model.pk == model_value.get("pk"):
                constructed_model = _construct_model(model_type, model_value)
                queryset._result_cache[idx] = constructed_model
                model_found = True

        if not model_found:
            constructed_model = _construct_model(model_type, model_value)
            queryset._result_cache.append(constructed_model)

    return queryset
