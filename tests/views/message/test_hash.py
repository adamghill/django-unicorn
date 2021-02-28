import shortuuid

from django_unicorn.utils import generate_checksum
from tests.views.fake_components import FakeComponent
from tests.views.message.test_calls import FakeCallsComponent
from tests.views.message.utils import post_and_get_response


def test_message_hash_no_change(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponent(
        component_id=component_id,
        component_name="tests.views.fake_components.FakeComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[
            {"payload": {"name": "test_method_kwargs(count=0)"}, "type": "callMethod",}
        ],
        component_id=component_id,
        hash=hash,
    )

    assert response.status_code == 304


def test_message_hash_changes(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponent(
        component_id=component_id,
        component_name="tests.views.fake_components.FakeComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[
            {"payload": {"name": "test_method_kwargs(count=1)"}, "type": "callMethod",}
        ],
        component_id=component_id,
        hash=hash,
    )

    assert response["data"]["method_count"] == 1


def test_message_hash_no_change_but_return_value(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponent(
        component_id=component_id,
        component_name="tests.views.fake_components.FakeComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[
            {"payload": {"name": "test_return_value"}, "type": "callMethod",}
        ],
        component_id=component_id,
        hash=hash,
    )

    # check that the response is JSON and not a 304
    assert isinstance(response, dict)
    assert response["return"]["value"]


def test_message_hash_no_change_but_return_redirect(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponent(
        component_id=component_id,
        component_name="tests.views.fake_components.FakeComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[{"payload": {"name": "test_redirect"}, "type": "callMethod",}],
        component_id=component_id,
        hash=hash,
    )

    # check that the response is JSON and not a 304
    assert isinstance(response, dict)
    assert response["return"]["value"]


def test_message_hash_no_change_but_return_hash_update(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponent(
        component_id=component_id,
        component_name="tests.views.fake_components.FakeComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[{"payload": {"name": "test_hash_update"}, "type": "callMethod",}],
        component_id=component_id,
        hash=hash,
    )

    # check that the response is JSON and not a 304
    assert isinstance(response, dict)
    assert response["return"]["value"]


def test_message_hash_no_change_but_return_poll_update(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponent(
        component_id=component_id,
        component_name="tests.views.fake_components.FakeComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[{"payload": {"name": "test_poll_update"}, "type": "callMethod",}],
        component_id=component_id,
        hash=hash,
    )

    # check that the response is JSON and not a 304
    assert isinstance(response, dict)
    assert response["return"]["value"]


def test_message_hash_no_change_but_return_location_update(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponent(
        component_id=component_id,
        component_name="tests.views.fake_components.FakeComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {"method_count": 0}
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=[
            {"payload": {"name": "test_refresh_redirect"}, "type": "callMethod",}
        ],
        component_id=component_id,
        hash=hash,
    )

    # check that the response is JSON and not a 304
    assert isinstance(response, dict)
    assert response["return"]["value"]


def test_message_hash_no_change_but_calls(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeCallsComponent(
        component_id=component_id,
        component_name="tests.views.message.test_calls.FakeCallsComponent",
    )
    rendered_content = component.render()
    hash = generate_checksum(rendered_content)

    data = {}
    response = post_and_get_response(
        client,
        url="/message/tests.views.message.test_calls.FakeCallsComponent",
        data=data,
        action_queue=[{"payload": {"name": "test_call"}, "type": "callMethod",}],
        component_id=component_id,
        hash=hash,
    )

    # check that the response is JSON and not a 304
    assert isinstance(response, dict)
    assert response.get("calls") == [{"args": [], "fn": "testCall"}]
