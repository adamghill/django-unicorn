import hmac
import logging
from collections.abc import Callable, Sequence, Set
from inspect import signature
from pprint import pprint
from typing import Dict, List, Optional, Union

import shortuuid
from django.conf import settings
from django.template import engines
from django.template.backends.django import Template
from django.utils.html import _json_script_escapes  # type: ignore
from django.utils.safestring import SafeText, mark_safe

try:
    from cachetools.lru import LRUCache
except ImportError:
    from cachetools import LRUCache


logger = logging.getLogger(__name__)

function_signature_cache = LRUCache(maxsize=100)


def generate_checksum(data: Union[bytes, str, Dict]) -> str:
    """Generates a checksum for the passed-in data.

    Args:
        data: The raw input to generate the checksum against.

    Returns:
        The generated checksum.
    """

    data_bytes: Optional[bytes] = None

    if isinstance(data, bytes):
        data_bytes = data
    elif isinstance(data, dict):
        data_bytes = str.encode(str(data))
    elif isinstance(data, str):
        data_bytes = str.encode(data)
    else:
        raise TypeError(f"Invalid type: {type(data)}")

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

    is_valid = all(k in dictionary_two and dictionary_one[k] == dictionary_two[k] for k in dictionary_one) and all(
        k in dictionary_one and dictionary_one[k] == dictionary_two[k] for k in dictionary_two
    )

    if not is_valid:
        print("dictionary_one:")  # noqa: T201
        pprint(dictionary_one)  # noqa: T203
        print()  # noqa: T201
        print("dictionary_two:")  # noqa: T201
        pprint(dictionary_two)  # noqa: T203

    return is_valid


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


def sanitize_html(html: str) -> SafeText:
    """
    Escape all the HTML/XML special characters with their unicode escapes, so
    value is safe to be output in JSON.

    This is the same internals as `django.utils.html.json_script` except it takes a string
    instead of an object to avoid calling DjangoJSONEncoder.
    """

    html = html.translate(_json_script_escapes)
    return mark_safe(html)  # noqa: S308


def is_non_string_sequence(obj):
    """
    Checks whether the object is a sequence (i.e. `list`, `tuple`, `set`), but _not_ `str` or `bytes` type.
    Helpful when you expect to loop over `obj`, but explicitly don't want to allow `str`.
    """

    if (isinstance(obj, (Sequence, Set))) and not isinstance(obj, (str, bytes, bytearray)):
        return True

    return False


def is_int(s: str) -> bool:
    """
    Checks whether a string is actually an integer.
    """

    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


def create_template(template_html: Union[str, Callable], engine_name: Optional[str] = None) -> Template:
    """Create a `Template` from a string or callable."""

    if callable(template_html):
        template_html = str(template_html())

    for engine in engines.all():
        if engine_name is None or engine_name == engine.name:
            try:
                return engine.from_string(template_html)  # type: ignore
            except NotImplementedError:
                pass

    raise AssertionError("Template could not be created based on configured template engines")
