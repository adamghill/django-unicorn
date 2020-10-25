import orjson
import pytest
from django.http import JsonResponse

from django_unicorn.components import ComponentLoadError
from django_unicorn.utils import generate_checksum
from django_unicorn.views import message
from example.coffee.models import Flavor


def assert_json_error(response, error):
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    assert response.json().get("error") == error


def post_json(client, data, url="/message/test"):
    return client.post(url, data, content_type="application/json")


def test_view_csrf(rf):
    request = rf.post("/message/test")
    response = message(request)
    assert response.status_code == 403


def test_message_component_name_is_none(client):
    response = client.post("/message")

    assert_json_error(response, "Missing component name in url")


def test_message_no_body(client):
    response = client.post("/message/test")

    assert_json_error(response, "Body could not be parsed")


def test_message_no_data(client):
    data = {}
    response = post_json(client, data)

    assert_json_error(response, "Invalid JSON body")


def test_message_no_checksum(client):
    data = {"data": {}, "id": "asdf"}
    response = post_json(client, data)

    assert_json_error(response, "Missing checksum")


def test_message_bad_checksum(client):
    data = {"data": {}, "checksum": "asdf", "id": "asdf"}
    response = post_json(client, data)

    assert_json_error(response, "Checksum does not match")


def test_message_no_component_id(client):
    data = {"data": {}, "checksum": "FpZ5q8E2"}
    response = post_json(client, data)

    assert_json_error(response, "Missing component id")


def test_message_component_not_found(client):
    data = {"data": {}, "checksum": "FpZ5q8E2", "id": "asdf"}

    with pytest.raises(ComponentLoadError) as e:
        post_json(client, data)

    assert (
        e.exconly()
        == "django_unicorn.components.ComponentLoadError: 'test' component could not be loaded."
    )


def test_message_nested_sync_input(client):
    data = {"dictionary": {"name": "test"}}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "dictionary.name", "value": "test1"},
                "type": "syncInput",
            }
        ],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": "FDHcbzGf",
    }

    response = post_json(
        client, message, url="/message/tests.views.components.TestComponent"
    )

    body = orjson.loads(response.content)

    assert body["id"] == "FDHcbzGf"
    assert not body["errors"]
    assert body["data"] == {"dictionary": {"name": "test1"}}


@pytest.mark.django_db
def test_message_db_input(client):
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

    response = post_json(
        client, message, url="/message/tests.views.components.TestModelComponent"
    )

    flavor = Flavor.objects.get(id=1)
    assert flavor.name == "Flowery-Floral"

    body = orjson.loads(response.content)

    assert not body["errors"]
    assert body["data"] == {
        "flavors": [{"pk": 1, "name": "Flowery-Floral", "label": "", "parent": None}]
    }
