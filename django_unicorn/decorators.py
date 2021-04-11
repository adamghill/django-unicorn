import logging
import time
import warnings

from django.conf import settings

from decorator import decorator


@decorator
def db_model(func, *args, **kwargs):
    """
    Converts a JSON representation of a Django model into an actual model.

    For example:
        @db_model
        def delete(self, model):
            ...

    Will get converted to:
        `component.delete({ 'name': 'modelName', pk: 1})` -> `component.delete(modelInstance)`
    """

    warnings.warn(
        "db_model is deprecated and will be removed in 0.28.0", stacklevel=2,
    )

    instance = args[0]
    model_dictionary = args[1]

    if hasattr(instance, "Meta") and hasattr(instance.Meta, "db_models"):
        db_model_name = model_dictionary.get("name")
        assert db_model_name, "Missing db model name"
        db_model_pk = model_dictionary.get("pk")
        assert db_model_pk, "Missing db model pk"
        db_model_found = False

        for db_model in instance.Meta.db_models:
            if db_model.name == db_model_name:
                model = db_model.model_class.objects.get(pk=db_model_pk)
                args = (instance, model,) + args[2:]
                db_model_found = True
                break

        assert db_model_found, f"No db_model found that matches '{db_model_name}'"
    else:
        raise AssertionError("No db_models defined")

    result = func(*args, **kwargs)

    return result


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
