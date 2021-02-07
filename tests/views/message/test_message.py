import time

from django.http import JsonResponse

import pytest

from django_unicorn.errors import ComponentLoadError
from django_unicorn.views import message


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
    data = {
        "data": {},
        "id": "asdf",
        "epoch": time.time(),
    }
    response = post_json(client, data)

    assert_json_error(response, "Missing checksum")


def test_message_bad_checksum(client):
    data = {
        "data": {},
        "checksum": "asdf",
        "id": "asdf",
        "epoch": time.time(),
    }
    response = post_json(client, data)

    assert_json_error(response, "Checksum does not match")


def test_message_no_component_id(client):
    data = {
        "data": {},
        "checksum": "FpZ5q8E2",
        "epoch": time.time(),
    }
    response = post_json(client, data)

    assert_json_error(response, "Missing component id")


def test_message_no_epoch(client):
    data = {"data": {}, "checksum": "FpZ5q8E2", "id": "abc"}
    response = post_json(client, data)

    assert_json_error(response, "Missing epoch")


def test_message_component_not_found(client):
    data = {
        "data": {},
        "checksum": "FpZ5q8E2",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentLoadError) as e:
        post_json(client, data)

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentLoadError: 'test' component could not be loaded."
    )


def test_message_component_with_dash(client):
    data = {
        "data": {},
        "checksum": "FpZ5q8E2",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentLoadError) as e:
        post_json(client, data, url="/message/test-a")

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentLoadError: 'test-a' component could not be loaded."
    )


def test_message_component_with_dot(client):
    data = {
        "data": {},
        "checksum": "FpZ5q8E2",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentLoadError) as e:
        post_json(client, data, url="/message/test.a")

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentLoadError: 'test.a' component could not be loaded."
    )
