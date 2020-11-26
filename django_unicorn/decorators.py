import logging
import time

from django.conf import settings

import wrapt


def _timed_enabled():
    return settings.DEBUG


@wrapt.decorator(enabled=_timed_enabled)
def timed(wrapped, instance, args, kwargs):
    """
    Decorator that prints out the timing of a function.

    Slightly altered version of https://gist.github.com/bradmontgomery/bd6288f09a24c06746bbe54afe4b8a82.
    """
    logger = logging.getLogger("profile")
    start = time.time()
    result = wrapped(*args, **kwargs)
    end = time.time()

    function_name = wrapped.__name__

    if instance:
        function_name = f"{instance}.{function_name}"

    arguments = ""

    if args:
        arguments = f"{args}, "

    for kwarg_key, kwarg_val in kwargs.items():
        if isinstance(kwarg_val, str):
            kwarg_val = f"'{kwarg_val}'"

        arguments = f"{arguments}{kwarg_key}={kwarg_val}, "

    if arguments.endswith(", "):
        arguments = arguments[:-2]

    ms = round(end - start, 4)

    logger.debug(f"{function_name}({arguments}): {ms}ms")
    return result
