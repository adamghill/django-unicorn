import logging
from dataclasses import is_dataclass
from datetime import date, datetime, time, timedelta, timezone
from inspect import signature
from typing import Dict, List, Union
from typing import get_type_hints as typing_get_type_hints
from uuid import UUID

from django.utils.dateparse import (
    parse_date,
    parse_datetime,
    parse_duration,
    parse_time,
)

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
    """
    Get type hints from an object. These get cached in a local memory cache for quicker look-up later.

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
    except TypeError:
        # Return an empty dictionary when there is a TypeError. From `get_type_hints`: "TypeError is
        # raised if the argument is not of a type that can contain annotations, and an empty dictionary
        # is returned if no annotations are present"
        return {}


def cast_value(type_hint, value):
    """
    Try to cast the value based on the type hint and
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

    for type_hint in type_hints:
        caster = CASTERS.get(type_hint)

        if caster:
            try:
                value = caster(value)
                break
            except TypeError:
                if (type_hint is datetime or type_hint is date) and (isinstance(value, (float, int))):
                    try:
                        value = datetime.fromtimestamp(value, tz=timezone.utc)

                        if type_hint is date:
                            value = value.date()

                        break
                    except ValueError:
                        pass
        else:
            value = type_hint(value)
            break

    return value


def cast_attribute_value(obj, name, value):
    """
    Try to cast the value of an object's attribute based on the type hint.
    """

    type_hints = get_type_hints(obj)
    type_hint = type_hints.get(name)

    if type_hint:
        if is_dataclass(type_hint):
            value = type_hint(**value)
        else:
            try:
                value = cast_value(type_hint, value)
            except TypeError:
                # Ignore this exception because some type-hints can't be instantiated like this (e.g. `List[]`)
                pass

    return value

def get_method_arguments(func) -> List[str]:
    """
    Gets the arguments for a method.

    Returns:
        A list of strings, one for each argument.
    """

    if func in function_signature_cache:
        return function_signature_cache[func]

    function_signature = signature(func)
    function_signature_cache[func] = list(function_signature.parameters)

    return function_signature_cache[func]
