import time

import orjson
import shortuuid

from django_unicorn.components import UnicornView, unicorn_view
from django_unicorn.utils import generate_checksum
from tests.views.message.utils import post_and_get_response


def test_message_call_method(client):
    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
            }
        ],
    )

    assert response["data"].get("method_count") == 1


def test_message_call_method_with_dictionary_checksum(client):
    data = {"dictionary": {"1": "test", "2": "anothertest", "3": "", "4": "moretest"}}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponentWithDictionary",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert not body["errors"]


def test_message_call_method_redirect(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_redirect"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert "redirect" in body
    redirect = body["redirect"]
    assert redirect.get("url") == "/something-here"
    assert redirect.get("refresh", False) is False


def test_message_call_method_with_message(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_message"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponentWithMessage",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert not body["errors"]

    assert "dom" in body
    dom = body["dom"]

    assert "test success" in dom


def test_message_call_method_redirect_with_message(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_redirect_with_message"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponentWithMessage",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert "redirect" in body
    redirect = body["redirect"]
    assert redirect.get("url") == "/something-here"
    assert redirect.get("refresh", False) is False

    assert "dom" in body
    dom = body["dom"]

    # Check that the message wasn't rendered out because redirects should defer messages until the next render
    assert "test success" not in dom

    # Check the private variable to ensure that there is a queue message for next render
    assert len(response.wsgi_request._messages._queued_messages) == 1


def test_message_call_method_refresh_redirect(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_refresh_redirect"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert "redirect" in body
    redirect = body["redirect"]
    assert redirect.get("url") == "/something-here"
    assert redirect.get("refresh")
    assert redirect.get("title") == "new title"


def test_message_call_method_hash_update(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_hash_update"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert "redirect" in body
    assert body["redirect"].get("hash") == "#test=1"


def test_message_call_method_return_value(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_return_value"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert "return" in body
    return_data = body["return"]
    assert return_data.get("method") == "test_return_value"
    assert return_data.get("args") == []
    assert return_data.get("kwargs") == {}
    assert return_data.get("value") == "booya"


def test_message_call_method_poll_update(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_poll_update"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert "poll" in body
    poll = body["poll"]
    assert poll.get("timing") == 1000
    assert poll.get("disable") == True
    assert poll.get("method") == "new_method"


def test_message_call_method_setter(client):
    data = {"method_count": 0}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "method_count=2"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("method_count") == 2


def test_message_call_method_nested_setter(client):
    data = {"nested": {"check": True}}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "nested.check=False"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("nested").get("check") == False


def test_message_call_method_multiple_nested_setter(client):
    data = {"nested": {"another": {"bool": True}}}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "nested.another.bool=False"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("nested").get("another").get("bool") == False


def test_message_call_method_toggle(client):
    data = {"check": False}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "$toggle('check')"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("check") == True


def test_message_call_method_nested_toggle(client):
    data = {"nested": {"check": False}}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "$toggle('nested.check')"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("nested").get("check") == True


def test_message_call_method_args(client):
    data = {"method_count": 0}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method_args(3)"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("method_count") == 3


def test_message_call_method_kwargs(client):
    data = {"method_count": 0}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method_kwargs(count=99)"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"].get("method_count") == 99


def test_message_call_method_no_validation(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "set_text_no_validation"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeValidationComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert not body["errors"]


def test_message_call_method_validation(client):
    data = {}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "set_text_with_validation"},
                "type": "callMethod",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeValidationComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["errors"]
    assert body["errors"]["number"]
    assert body["errors"]["number"][0]["code"] == "required"
    assert body["errors"]["number"][0]["message"] == "This field is required."


def test_message_call_method_reset(client):
    data = {"method_count": 1}
    message = {
        "actionQueue": [
            {"payload": {"name": "method_count=2"}, "type": "callMethod"},
            {
                "payload": {"name": "$reset"},
                "type": "callMethod",
            },
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"]["method_count"] == 0
    # `data` should contain all data (not just the diffs) for resets
    assert body["data"].get("check") is not None
    assert body["data"].get("dictionary") is not None


def test_message_call_method_refresh(client):
    data = {"method_count": 1}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "$refresh"},
                "type": "callMethod",
            },
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.fake_components.FakeComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)

    assert body["data"]["method_count"] == 1
    # `data` should contain all data (not just the diffs) for refreshes
    assert body["data"].get("check") is not None
    assert body["data"].get("dictionary") is not None


def test_message_call_method_caches_disabled(client, monkeypatch, settings):
    monkeypatch.setattr(unicorn_view, "COMPONENTS_MODULE_CACHE_ENABLED", False)
    settings.CACHES["default"][
        "BACKEND"
    ] = "django.core.cache.backends.dummy.DummyCache"

    component_id = shortuuid.uuid()[:8]
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data={"method_count": 0},
        action_queue=[
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
            }
        ],
        component_id=component_id,
    )

    method_count = response["data"].get("method_count")

    assert method_count == 1

    # Get the component again
    view = UnicornView.create(
        component_name="tests.views.fake_components.FakeComponent",
        component_id=component_id,
        use_cache=True,
    )

    # Component is not retrieved from any caches
    assert view.method_count == 0


def test_message_call_method_module_cache_disabled(client, monkeypatch, settings):
    monkeypatch.setattr(unicorn_view, "COMPONENTS_MODULE_CACHE_ENABLED", False)
    settings.UNICORN["CACHE_ALIAS"] = "default"
    settings.CACHES["default"][
        "BACKEND"
    ] = "django.core.cache.backends.locmem.LocMemCache"

    component_id = shortuuid.uuid()[:8]
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data={"method_count": 0},
        action_queue=[
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
            }
        ],
        component_id=component_id,
    )

    method_count = response["data"].get("method_count")

    assert method_count == 1

    # Get the component again and it should be found in local memory cache
    view = UnicornView.create(
        component_name="tests.views.fake_components.FakeComponent",
        component_id=component_id,
        use_cache=True,
    )

    # Component is retrieved from the local memory cache
    assert view.method_count == method_count


def test_message_call_method_cache_backend_dummy(client, monkeypatch, settings):
    monkeypatch.setattr(unicorn_view, "COMPONENTS_MODULE_CACHE_ENABLED", True)
    settings.CACHES["default"][
        "BACKEND"
    ] = "django.core.cache.backends.dummy.DummyCache"

    component_id = shortuuid.uuid()[:8]
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data={"method_count": 0},
        action_queue=[
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
            }
        ],
        component_id=component_id,
    )

    method_count = response["data"].get("method_count")

    assert method_count == 1

    # Get the component again and it should be found in local memory cache
    view = UnicornView.create(
        component_name="tests.views.fake_components.FakeComponent",
        component_id=component_id,
        use_cache=True,
    )

    # Component is retrieved from the module cache
    assert view.method_count == method_count
