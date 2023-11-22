import time

import orjson
import shortuuid

from django_unicorn.utils import generate_checksum


def _post_message_and_get_body(client, message, url="/message/tests.views.fake_components.FakeComponent"):
    response = client.post(
        url,
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)
    return body


def test_setter(client):
    data = {"nested": {"check": False}, "check": False}
    message = {
        "actionQueue": [
            {"type": "callMethod", "payload": {"name": "check=True"}},
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    body = _post_message_and_get_body(client, message)

    assert not body["errors"]
    assert body["data"]["check"] is True


def test_setter_updated(client):
    data = {"count": 1, "count_updating": 0, "count_updated": 0}
    message = {
        "actionQueue": [
            {"type": "callMethod", "payload": {"name": "count=2"}},
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    body = _post_message_and_get_body(
        client,
        message,
        url="/message/tests.views.fake_components.FakeComponentWithUpdateMethods",
    )

    assert not body["errors"]
    assert body["data"]["count"] == 2

    # If updating_count or updated_count is called more than once
    # `FakeComponentWithUpdateMethods` will raise an exception


def test_nested_setter(client):
    data = {"nested": {"check": False}}
    message = {
        "actionQueue": [
            {"type": "callMethod", "payload": {"name": "nested.check=True"}},
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    body = _post_message_and_get_body(client, message)

    assert not body["errors"]
    assert body["data"]["nested"]["check"] is True


def test_equal_sign(client):
    data = {"nested": {"check": False}, "method_arg": ""}
    message = {
        "actionQueue": [
            {
                "type": "callMethod",
                "payload": {"name": "test_method_string_arg('does=thiswork?')"},
            },
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    body = _post_message_and_get_body(client, message)

    assert not body["errors"]
    assert body["data"]["method_arg"] == "does=thiswork?"
