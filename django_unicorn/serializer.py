import logging
from decimal import Decimal
from functools import lru_cache
from typing import Dict, List

from django.core.serializers import serialize
from django.db.models import (
    DateField,
    DateTimeField,
    DurationField,
    Model,
    QuerySet,
    TimeField,
)
from django.utils.dateparse import (
    parse_date,
    parse_datetime,
    parse_duration,
    parse_time,
)

import orjson


try:
    from pydantic import BaseModel as PydanticBaseModel
except ImportError:
    PydanticBaseModel = None


logger = logging.getLogger(__name__)


class JSONDecodeError(Exception):
    pass


def _parse_field_values_from_string(model: Model) -> None:
    """
    Convert the model fields' value to match the field type if appropriate.

    This is mostly to deal with field string values that will get saved as a date-related field.
    """

    for field in model._meta.fields:
        val = getattr(model, field.attname)

        if not isinstance(val, str):
            continue

        if isinstance(field, DateTimeField):
            setattr(model, field.attname, parse_datetime(val))
        elif isinstance(field, TimeField):
            setattr(model, field.attname, parse_time(val))
        elif isinstance(field, DateField):
            setattr(model, field.attname, parse_date(val))
        elif isinstance(field, DurationField):
            setattr(model, field.attname, parse_duration(val))


def _get_model_dict(model: Model) -> dict:
    """
    Serializes Django models. Uses the built-in Django JSON serializer, but moves the data around to
    remove some unnecessary information and make the structure more compact.
    """

    _parse_field_values_from_string(model)

    # Django's `serialize` method always returns an array, so remove the brackets from the resulting string
    serialized_model = serialize("json", [model])[1:-1]
    model_json = orjson.loads(serialized_model)
    model_pk = model_json.get("pk")
    model_json = model_json.get("fields")
    model_json["pk"] = model_pk

    for field in model._meta.get_fields():
        if field.is_relation and field.many_to_many:
            related_name = field.name

            if field.auto_created:
                related_name = field.related_name or f"{field.name}_set"

            pks = []

            try:
                related_descriptor = getattr(model, related_name)
                pks = list(related_descriptor.values_list("pk", flat=True))
            except ValueError:
                # ValueError is throuwn when the model doesn't have an id already set
                pass

            model_json[related_name] = pks

    return model_json


def _json_serializer(obj):
    """
    Handle the objects that the `orjson` deserializer can't handle automatically.

    The types handled by `orjson` by default: dataclass, datetime, enum, float, int, numpy, str, uuid.
    The types handled in this class: Django Model, Django QuerySet, Decimal, or any object with `to_json` method.

    TODO: Investigate other ways to serialize objects automatically.
    e.g. Using DRF serializer: https://www.django-rest-framework.org/api-guide/serializers/#serializing-objects
    """
    from .components import UnicornView

    try:
        if isinstance(obj, UnicornView):
            return {
                "name": obj.component_name,
                "id": obj.component_id,
                "key": obj.component_key,
            }
        elif isinstance(obj, Model):
            return _get_model_dict(obj)
        elif isinstance(obj, QuerySet):
            queryset_json = []

            for model in obj:
                if obj.query.values_select and isinstance(model, dict):
                    # If the queryset was created with values it's already a dictionary
                    model_json = model
                else:
                    model_json = _get_model_dict(model)

                queryset_json.append(model_json)

            return queryset_json
        elif PydanticBaseModel and isinstance(obj, PydanticBaseModel):
            return obj.dict()
        elif isinstance(obj, Decimal):
            return str(obj)
        elif hasattr(obj, "to_json"):
            return obj.to_json()
    except Exception as e:
        # Log this because the `TypeError` and resulting stacktrace lacks context
        logger.exception(e)

    raise TypeError


def _fix_floats(current: Dict, data: Dict = None, paths: List = []) -> None:
    """
    Recursively change any Python floats to a string so that JavaScript
    won't convert the float to an integer when deserializing.

    Params:
        current: Dictionary in which to check for and fix floats.
    """

    if data is None:
        data = current

    if isinstance(current, dict):
        for key, val in current.items():
            paths.append(key)
            _fix_floats(val, data, paths=paths)
            paths.pop()
    elif isinstance(current, list):
        for (idx, item) in enumerate(current):
            paths.append(idx)
            _fix_floats(item, data, paths=paths)
            paths.pop()
    elif isinstance(current, float):
        _piece = data

        for (idx, path) in enumerate(paths):
            if idx == len(paths) - 1:
                # `path` can be a dictionary key or list index,
                # but in either instance it is set the same way
                _piece[path] = str(current)
            else:
                _piece = _piece[path]


@lru_cache(maxsize=128)
def _dumps(serialized_data):
    dict_data = orjson.loads(serialized_data)
    _fix_floats(dict_data)

    dumped_data = orjson.dumps(dict_data).decode("utf-8")
    return dumped_data


def dumps(data: dict, fix_floats: bool = True) -> str:
    """
    Converts the passed-in dictionary to a string representation.

    Handles the following objects: dataclass, datetime, enum, float, int, numpy, str, uuid,
    Django Model, Django QuerySet, any object with `to_json` method.

    Args:
        param fix_floats: Whether any floats should be converted to strings. Defaults to `True`,
            but will be faster without it.
    
    Returns a string which deviates from `orjson.dumps`, but seems more useful.
    """

    serialized_data = orjson.dumps(data, default=_json_serializer)

    if fix_floats:
        return _dumps(serialized_data)

    return serialized_data.decode("utf-8")


def loads(str: str) -> dict:
    """
    Converts a string representation to dictionary.
    """

    try:
        return orjson.loads(str)
    except orjson.JSONDecodeError as e:
        raise JSONDecodeError from e


def model_value(model: Model, *fields: str):
    """
    Serializes a model into a dictionary with the fields as specified in the `fields` argument.
    """

    model_data = {}
    model_dict = _get_model_dict(model)

    if not fields:
        return model_dict

    for field in fields:
        if field in model_dict:
            model_data[field] = model_dict[field]

    return model_data
