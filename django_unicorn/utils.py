import hmac
import logging
import pickle

from django.conf import settings

import shortuuid

from django_unicorn.errors import UnicornCacheError


logger = logging.getLogger(__name__)


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

    return component
