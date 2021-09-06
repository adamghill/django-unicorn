import logging
import time

from django.conf import settings

from decorator import decorator


@decorator
def timed(func, *args, **kwargs):
    """
    Decorator that prints out the timing of a function.

    Slightly altered version of https://gist.github.com/bradmontgomery/bd6288f09a24c06746bbe54afe4b8a82.
    """
    if not settings.DEBUG:
        return func(*args, **kwargs)

    logger = logging.getLogger("profile")
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()

    function_name = func.__name__
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
