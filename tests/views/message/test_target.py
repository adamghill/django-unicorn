import time

import shortuuid
from bs4 import BeautifulSoup

from django_unicorn.components import UnicornView
from django_unicorn.utils import generate_checksum


class FakeTargetComponent(UnicornView):
    template_name = "templates/test_component_target.html"

    clicked = False

    def test_method(self):
        self.clicked = True


def test_message_generated_checksum_matches_dom_checksum(client):
    data = {"clicked": False}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
                "target": None,
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.message.test_target.FakeTargetComponent",
        message,
        content_type="application/json",
    )

    body = response.json()
    dom = body.get("dom")

    assert dom
    assert not body.get("partials")
    assert body.get("data", {}).get("clicked") is True

    soup = BeautifulSoup(dom, features="html.parser")

    for element in soup.find_all():
        if "unicorn:checksum" in element.attrs:
            assert element.attrs["unicorn:checksum"] == body.get("checksum")
            break


def test_message_target_invalid(client):
    data = {"clicked": False}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
                "target": "test-target-id1",
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.message.test_target.FakeTargetComponent",
        message,
        content_type="application/json",
    )

    body = response.json()

    assert body.get("dom")
    assert not body.get("partials")
    assert body.get("data", {}).get("clicked") is True


def test_message_target_id(client):
    data = {"clicked": False}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
                "partial": {"target": "test-target-id"},
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.message.test_target.FakeTargetComponent",
        message,
        content_type="application/json",
    )

    body = response.json()

    assert body.get("dom") is None
    assert len(body["partials"]) == 1
    assert body["partials"][0]["id"] == "test-target-id"
    assert body["partials"][0]["dom"] == '<div id="test-target-id"></div>'
    assert body.get("data", {}).get("clicked") is True


def test_message_target_only_id(client):
    data = {"clicked": False}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
                "partial": {"id": "test-target-id"},
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.message.test_target.FakeTargetComponent",
        message,
        content_type="application/json",
    )

    body = response.json()

    assert body.get("dom") is None
    assert len(body["partials"]) == 1
    assert body["partials"][0]["id"] == "test-target-id"
    assert body["partials"][0]["dom"] == '<div id="test-target-id"></div>'
    assert body.get("data", {}).get("clicked") is True


def test_message_target_only_key(client):
    data = {"clicked": False}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
                "partial": {"key": "test-target-key"},
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.message.test_target.FakeTargetComponent",
        message,
        content_type="application/json",
    )

    body = response.json()

    assert body.get("dom") is None
    assert len(body["partials"]) == 1
    assert body["partials"][0]["key"] == "test-target-key"
    assert body["partials"][0]["dom"] == '<div unicorn:key="test-target-key"></div>'
    assert body.get("data", {}).get("clicked") is True


def test_message_target_key(client):
    data = {"clicked": False}
    message = {
        "actionQueue": [
            {
                "payload": {"name": "test_method"},
                "type": "callMethod",
                "partial": {"target": "test-target-key"},
            }
        ],
        "data": data,
        "checksum": generate_checksum(str(data)),
        "id": shortuuid.uuid()[:8],
        "epoch": time.time(),
    }

    response = client.post(
        "/message/tests.views.message.test_target.FakeTargetComponent",
        message,
        content_type="application/json",
    )

    body = response.json()

    assert body.get("dom") is None
    assert len(body["partials"]) == 1
    assert body["partials"][0]["key"] == "test-target-key"
    assert body["partials"][0]["dom"] == '<div unicorn:key="test-target-key"></div>'
    assert body.get("data", {}).get("clicked") is True
