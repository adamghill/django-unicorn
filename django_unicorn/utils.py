import collections.abc
import hmac
import logging
import pickle
from inspect import signature
from pprint import pprint
from typing import Dict, List, Union
from typing import get_type_hints as typing_get_type_hints

from django.conf import settings
from django.utils.html import _json_script_escapes
from django.utils.safestring import mark_safe

import shortuuid

import django_unicorn
from django_unicorn.errors import UnicornCacheError


try:
    from cachetools.lru import LRUCache
except ImportError:
    from cachetools import LRUCache


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
        str.encode(settings.SECRET_KEY),
        data_bytes,
        digestmod="sha256",
    ).hexdigest()
    checksum = shortuuid.uuid(checksum)[:8]

    return checksum


def dicts_equal(dictionary_one: Dict, dictionary_two: Dict) -> bool:
    """
    Return True if all keys and values are the same between two dictionaries.
    """

    is_valid = all(
        k in dictionary_two and dictionary_one[k] == dictionary_two[k]
        for k in dictionary_one
    ) and all(
        k in dictionary_one and dictionary_one[k] == dictionary_two[k]
        for k in dictionary_two
    )

    if not is_valid:
        print("dictionary_one:")
        pprint(dictionary_one)
        print()
        print("dictionary_two:")
        pprint(dictionary_two)

    return is_valid


class CacheableComponent:
    """
    Updates a component into something that is cacheable/pickleable. Use in a `with` statement
    or explicitly call `__enter__` `__exit__` to use. It will restore the original component
    on exit.
    """
    def __init__(self, component: "django_unicorn.views.UnicornView"):
        self._state = {}
        self.cacheable_component = component

    def __enter__(self):
        components = []
        components.append(self.cacheable_component)
        while components:
            component = components.pop()
            if component.component_id in self._state:
                continue
            if hasattr(component, 'extra_context'):
                extra_context = component.extra_context
                component.extra_context = None
            else:
                extra_context = None
            request = component.request
            component.request = None
            self._state[component.component_id] = (component, request, extra_context)
            if component.parent:
                components.append(component.parent)
            for child in component.children:
                components.append(child)

        for component, _, _ in self._state.values():
            try:
                pickle.dumps(component)
            except (TypeError, AttributeError, NotImplementedError, pickle.PicklingError) as e:
                raise UnicornCacheError(
                    f"Cannot cache component '{type(component)}' because it is not picklable: {type(e)}: {e}"
                ) from e

    def __exit__(self, *args):
        for component, request, extra_context in self._state.values():
            component.request = request
            if extra_context:
                component.extra_context = extra_context


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


def is_non_string_sequence(obj):
    """
    Checks whether the object is a sequence (i.e. `list`, `tuple`, `set`), but _not_ `str` or `bytes` type.
    Helpful when you expect to loop over `obj`, but explicitly don't want to allow `str`.
    """

    if (
        isinstance(obj, collections.abc.Sequence)
        or isinstance(obj, collections.abc.Set)
    ) and not isinstance(obj, (str, collections.abc.ByteString)):
        return True

    return False
