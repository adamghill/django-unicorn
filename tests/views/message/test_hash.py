import shortuuid

from django_unicorn.components import UnicornView
from django_unicorn.utils import generate_checksum
from tests.views.fake_components import FakeComponent
from tests.views.message.test_calls import FakeCallsComponent
from tests.views.message.utils import post_and_get_response


class FakeComponentParent(UnicornView):
    template_name = "templates/test_component_parent_with_value.html"

    value: int = 0


class FakeComponentChild(UnicornView):
    template_name = "templates/test_component_child.html"

    def parent_increment(self):
        self.parent.value += 1


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
            {
                "payload": {"name": "test_method_kwargs(count=0)"},
                "type": "callMethod",
            }
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
            {
                "payload": {"name": "test_method_kwargs(count=1)"},
                "type": "callMethod",
            }
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
            {
                "payload": {"name": "test_return_value"},
                "type": "callMethod",
            }
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
        action_queue=[
            {
                "payload": {"name": "test_redirect"},
                "type": "callMethod",
            }
        ],
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
        action_queue=[
            {
                "payload": {"name": "test_hash_update"},
                "type": "callMethod",
            }
        ],
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
        action_queue=[
            {
                "payload": {"name": "test_poll_update"},
                "type": "callMethod",
            }
        ],
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
            {
                "payload": {"name": "test_refresh_redirect"},
                "type": "callMethod",
            }
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
        action_queue=[
            {
                "payload": {"name": "test_call"},
                "type": "callMethod",
            }
        ],
        component_id=component_id,
        hash=hash,
    )

    # check that the response is JSON and not a 304
    assert isinstance(response, dict)
    assert response.get("calls") == [{"args": [], "fn": "testCall"}]


def test_message_hash_no_change_but_parent(client):
    component_id = shortuuid.uuid()[:8]
    component = FakeComponentParent(
        component_id=component_id,
        component_name="tests.views.message.test_hash.FakeComponentParent",
    )
    component.render()

    child = component.children[0]
    rendered_child_content = child.render()
    child_hash = generate_checksum(rendered_child_content)

    assert child.parent.value == 0

    data = {}
    response = post_and_get_response(
        client,
        url="/message/tests.views.message.test_hash.FakeComponentChild",
        data=data,
        action_queue=[
            {
                "payload": {"name": "parent_increment()"},
                "type": "callMethod",
            }
        ],
        component_id=child.component_id,
        hash=child_hash,
        return_response=True,
    )

    assert response.status_code == 200
    assert child.parent.value == 1

    rendered_parent_content = child.parent.render()
    assert "||value:1||" in rendered_parent_content
