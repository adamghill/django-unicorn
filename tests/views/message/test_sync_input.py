import orjson

from django_unicorn.utils import generate_checksum


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

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert not body["errors"]
    assert body["data"].get("dictionary") == {"name": "test1"}
