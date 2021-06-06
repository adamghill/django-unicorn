import hmac
import logging
import pickle
from inspect import signature
from typing import Dict, List, Union
from typing import get_type_hints as typing_get_type_hints

from django.conf import settings
from django.utils.html import _json_script_escapes, format_html
from django.utils.safestring import mark_safe

import shortuuid
from cachetools.lru import LRUCache

import django_unicorn
from django_unicorn.errors import UnicornCacheError


logger = logging.getLogger(__name__)

type_hints_cache = LRUCache(maxsize=100)
function_signature_cache = LRUCache(maxsize=100)


def generate_checksum(data: Union[str, bytes]) -> str:
    """
    Generates a checksum for the passed-in data.
    """

    if isinstance(data, str):
        data_bytes = str.encode(data)
    else:
        data_bytes = data

    checksum = hmac.new(
        str.encode(settings.SECRET_KEY), data_bytes, digestmod="sha256",
    ).hexdigest()
    checksum = shortuuid.uuid(checksum)[:8]

    return checksum


def dicts_equal(dictionary_one: Dict, dictionary_two: Dict) -> bool:
    """
    Return True if all keys and values are the same between two dictionaries.
    """

    return all(
        k in dictionary_two and dictionary_one[k] == dictionary_two[k]
        for k in dictionary_one
    ) and all(
        k in dictionary_one and dictionary_one[k] == dictionary_two[k]
        for k in dictionary_two
    )


def get_cacheable_component(
    component: "django_unicorn.views.UnicornView",
) -> "django_unicorn.views.UnicornView":
    """
    Converts a component into something that is cacheable/pickleable.
    """

    component.request = None

    if component.parent:
        component.parent = get_cacheable_component(component.parent)

    try:
        pickle.dumps(component)
    except TypeError as e:
        raise UnicornCacheError(
            "Cannot cache component because it is not picklable."
        ) from e
    except AttributeError as e:
        raise UnicornCacheError(
            "Cannot cache component because it is not picklable."
        ) from e
    except NotImplementedError as e:
        raise UnicornCacheError(
            "Cannot cache component because it is not picklable."
        ) from e
    except pickle.PicklingError as e:
        raise UnicornCacheError(
            "Cannot cache component because it is not picklable."
        ) from e

    return component


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


def sanitize_html(str):
    """
    Escape all the HTML/XML special characters with their unicode escapes, so
    value is safe to be output in JSON.

    This is the same internals as `django.utils.html.json_script` except it takes a string
    instead of an object to avoid calling DjangoJSONEncoder.
    """

    str = str.translate(_json_script_escapes)
    return mark_safe(str)
