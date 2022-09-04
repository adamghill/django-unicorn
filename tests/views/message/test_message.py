import time

from django.http import JsonResponse

import pytest

from django_unicorn.errors import ComponentClassLoadError, ComponentModuleLoadError
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
        "checksum": "DVVk97cx",
        "epoch": time.time(),
    }
    response = post_json(client, data)

    assert_json_error(response, "Missing component id")


def test_message_no_epoch(client):
    data = {"data": {}, "checksum": "DVVk97cx", "id": "abc"}
    response = post_json(client, data)

    assert_json_error(response, "Missing epoch")


def test_message_component_module_not_loaded(client):
    data = {
        "data": {},
        "checksum": "DVVk97cx",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentModuleLoadError) as e:
        post_json(client, data)

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentModuleLoadError: The component module 'test' could not be loaded."
    )
    assert e.value.locations == [("unicorn.components.test", "TestView")]


def test_message_component_class_not_loaded(client):
    data = {
        "data": {},
        "checksum": "DVVk97cx",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentClassLoadError) as e:
        post_json(
            client,
            data,
            url="/message/tests.views.fake_components.FakeComponentNotThere",
        )

    print(e.value.locations)
    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentClassLoadError: The component class 'tests.views.fake_components.FakeComponentNotThere' could not be loaded."
    )
    assert e.value.locations == [
        ("tests.views.fake_components", "FakeComponentNotThere"),
        (
            "unicorn.components.tests.views.fake_components.FakeComponentNotThere",
            "FakecomponentnotthereView",
        ),
    ]


def test_message_component_class_with_attribute_error(client):
    data = {
        "data": {},
        "checksum": "DVVk97cx",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentClassLoadError) as e:
        post_json(
            client,
            data,
            url="/message/tests.views.fake_components.FakeComponentWithError",
        )

    assert e.value.__cause__


def test_message_component_with_dash(client):
    data = {
        "data": {},
        "checksum": "DVVk97cx",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentModuleLoadError) as e:
        post_json(client, data, url="/message/test-a")

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentModuleLoadError: The component module 'test_a' could not be loaded."
    )


def test_message_component_with_dot(client):
    data = {
        "data": {},
        "checksum": "DVVk97cx",
        "id": "asdf",
        "epoch": time.time(),
    }

    with pytest.raises(ComponentClassLoadError) as e:
        post_json(client, data, url="/message/test.a")

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentClassLoadError: The component class 'test.a' could not be loaded."
    )
