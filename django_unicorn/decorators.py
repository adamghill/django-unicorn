import logging
import time

from django.conf import settings

import wrapt


@wrapt.decorator()
def db_model(wrapped, instance, args, kwargs):
    """
    Converts a JSON representation of a Django model into an actual model.

    For example:
        @db_model
        def delete(self, model):
            ...
    
    Will get converted to:
        `component.delete({ 'name': 'modelName', pk: 1})` -> `component.delete(modelInstance)`
    """

    if hasattr(instance, "Meta") and hasattr(instance.Meta, "db_models"):
        db_model_name = args[0].get("name")
        assert db_model_name, "Missing db model name"
        db_model_pk = args[0].get("pk")
        assert db_model_pk, "Missing db model pk"
        db_model_found = False

        for db_model in instance.Meta.db_models:
            if db_model.name == db_model_name:
                model = db_model.model_class.objects.get(pk=db_model_pk)
                args = (model,) + args[1:]
                db_model_found = True
                break

        assert db_model_found, f"No db_model found that matches '{db_model_name}'"
    else:
        raise AssertionError("No db_models defined")

    result = wrapped(*args, **kwargs)

    return result


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
