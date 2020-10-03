from typing import Any

import orjson
from django.core.serializers import serialize
from django.db.models import Model, QuerySet


def _get_model_dict(obj: Any) -> dict:
    """
    Serializes Django models.
    """

    # Django's serialize always returns an array, so remove that from the string
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
    if isinstance(obj, Model):
        return _get_model_dict(obj)
    elif isinstance(obj, QuerySet):
        queryset_json = []

        for model in obj:
            model_json = _get_model_dict(model)
            queryset_json.append(model_json)

        return queryset_json
    elif hasattr(obj, "to_json"):
        return obj.to_json()

    raise TypeError


def dumps(data: dict) -> str:
    dumped_data = orjson.dumps(data, default=_json_serializer).decode("utf-8")

    return dumped_data
