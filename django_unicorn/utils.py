import hmac
import logging
import pickle
from typing import get_type_hints as typing_get_type_hints

from django.conf import settings

import shortuuid
from cachetools.lru import LRUCache

from django_unicorn.errors import UnicornCacheError


logger = logging.getLogger(__name__)

type_hints_cache = LRUCache(maxsize=100)


def generate_checksum(data):
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


def dicts_equal(dictionary_one, dictionary_two):
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


def get_cacheable_component(component):
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


def get_type_hints(obj):
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
