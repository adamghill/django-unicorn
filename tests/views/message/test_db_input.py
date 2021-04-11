import time

import orjson
import pytest
import shortuuid

from django_unicorn.utils import dicts_equal, generate_checksum
from example.coffee.models import Flavor


@pytest.mark.django_db
def test_message_db_input_update(client):
    flavor = Flavor(id=1, name="Enzymatic-Flowery")
    flavor.save()
    data = {"flavors": [{"pk": flavor.pk, "name": flavor.name}]}

    message = {
        "actionQueue": [
            {
                "payload": {
                    "model": "flavors",
                    "db": {"pk": flavor.pk, "name": "flavor"},
                    "fields": {"name": "Flowery-Floral"},
                },
                "type": "dbInput",
            },
            {"type": "callMethod", "payload": {"name": "$refresh", "params": []}},
        ],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeModelComponent",
        message,
        content_type="application/json",
    )

    flavor = Flavor.objects.get(id=1)
    assert flavor.name == "Flowery-Floral"

    body = orjson.loads(response.content)

    assert not body["errors"]
    expected = {
        "flavors": [
            {
                "pk": 1,
                "name": "Flowery-Floral",
                "decimal_value": None,
                "float_value": None,
                "label": "",
                "parent": None,
                "uuid": str(flavor.uuid),
                "datetime": None,
                "date": None,
                "time": None,
                "duration": None,
                "taste_set": [],
                "origins": [],
            }
        ]
    }

    assert dicts_equal(expected, body["data"])


@pytest.mark.django_db
def test_message_db_input_create(client):
    data = {"flavors": []}

    message = {
        "actionQueue": [
            {
                "payload": {
                    "model": "flavors",
                    "db": {"pk": "", "name": "flavor"},
                    "fields": {"name": "Sugar Browning-Nutty"},
                },
                "type": "dbInput",
            },
            {"type": "callMethod", "payload": {"name": "$refresh", "params": []}},
        ],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    assert Flavor.objects.all().count() == 0

    response = client.post(
        "/message/tests.views.fake_components.FakeModelComponent",
        message,
        content_type="application/json",
    )

    flavor = Flavor.objects.get(id=1)
    assert flavor.name == "Sugar Browning-Nutty"

    body = orjson.loads(response.content)

    expected = {
        "flavors": [
            {
                "name": "Sugar Browning-Nutty",
                "label": "",
                "parent": None,
                "float_value": None,
                "decimal_value": None,
                "uuid": str(flavor.uuid),
                "datetime": None,
                "date": None,
                "time": None,
                "duration": None,
                "pk": 1,
                "taste_set": [],
                "origins": [],
            }
        ]
    }

    assert not body["errors"]
    assert dicts_equal(expected, body["data"])
