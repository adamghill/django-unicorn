import orjson

from django_unicorn.utils import generate_checksum


def test_message_call_method(client):
    data = {}
    message = {
        "actionQueue": [
            {"payload": {"name": "refresh", "params": []}, "type": "callMethod",}
        ],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": "FDHcbzGf",
    }

    response = client.post(
        "/message/tests.views.fake_components.TestComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("dictionary") == {"name": "test"}


def test_message_call_method(client):
    data = {}
    message = {
        "actionQueue": [
            {"payload": {"name": "test_method", "params": []}, "type": "callMethod",}
        ],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": "FDHcbzGf",
    }

    response = client.post(
        "/message/tests.views.fake_components.TestComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("method_count") == 1
