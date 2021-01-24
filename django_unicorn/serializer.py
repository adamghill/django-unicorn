from functools import lru_cache
from typing import Any, Dict, List

from django.core.serializers import serialize
from django.db.models import Model, QuerySet


try:
    from pydantic import BaseModel as PydanticBaseModel
except ImportError:
    PydanticBaseModel = None

import orjson


class JSONDecodeError(Exception):
    pass


def _get_model_dict(obj: Any) -> dict:
    """
    Serializes Django models. Uses the built-in Django JSON serializer, but moves the data around to
    remove some unnecessary information and make the structure more compact.
    """

    # Django's serialize always returns an array, so remove the brackets from the string
    serialized_model = serialize("json", [obj])[1:-1]
    model_json = orjson.loads(serialized_model)
    model_pk = model_json.get("pk")
    model_json = model_json.get("fields")
    model_json["pk"] = model_pk

    return model_json


def _json_serializer(obj):
    """
    Handle the objects that the `orjson` deserializer can't handle automatically.

    The types handled by `orjson` by default: dataclass, datetime, enum, float, int, numpy, str, uuid.
    The types handled in this class: Django Model, Django QuerySet, any object with `to_json` method.

    TODO: Investigate other ways to serialize objects automatically.
    e.g. Using DRF serializer: https://www.django-rest-framework.org/api-guide/serializers/#serializing-objects
    """
    from .components import UnicornView

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
            model_json = _get_model_dict(model)
            queryset_json.append(model_json)

        return queryset_json
    elif PydanticBaseModel and isinstance(obj, PydanticBaseModel):
        return obj.dict()
    elif hasattr(obj, "to_json"):
        return obj.to_json()

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
    """

    serialized_data = orjson.dumps(data, default=_json_serializer)

    if fix_floats:
        return _dumps(serialized_data)

    return serialized_data


def loads(str: str) -> dict:
    """
    Converts a string representation to dictionary.
    """

    try:
        return orjson.loads(str)
    except orjson.JSONDecodeError as e:
        raise JSONDecodeError from e
