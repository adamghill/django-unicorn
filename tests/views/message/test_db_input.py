import orjson
import pytest

from django_unicorn.utils import generate_checksum
from example.coffee.models import Flavor


@pytest.mark.django_db
def test_message_db_input_update(client):
    flavor = Flavor(id=1, name="Enzymatic-Flowery")
    flavor.save()
    data = {"flavors": [{"pk": flavor.pk, "title": flavor.name}]}

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
            {"type": "callMethod", "payload": {"name": "refresh", "params": []}},
        ],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": "FDHcbzGf",
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
    assert body["data"] == {
        "flavors": [{"pk": 1, "name": "Flowery-Floral", "label": "", "parent": None}]
    }


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
            {"type": "callMethod", "payload": {"name": "refresh", "params": []}},
        ],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": "FDHcbzGf",
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

    assert not body["errors"]
    assert body["data"] == {
        "flavors": [
            {"pk": 1, "name": "Sugar Browning-Nutty", "label": "", "parent": None}
        ]
    }
