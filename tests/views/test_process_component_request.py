from tests.views.message.utils import post_and_get_response

from django_unicorn.components import UnicornView


class FakeComponent(UnicornView):
    template_name = "templates/test_component_variable.html"

    hello = ""


class FakeComponentSafe(UnicornView):
    template_name = "templates/test_component_variable.html"

    hello = ""

    class Meta:
        safe = ("hello",)


def test_html_entities_encoded(client):
    data = {"hello": "test"}
    action_queue = [
        {
            "payload": {"name": "hello", "value": "<b>test1</b>"},
            "type": "syncInput",
        }
    ]
    response = post_and_get_response(
        client,
        url="/message/tests.views.test_process_component_request.FakeComponent",
        data=data,
        action_queue=action_queue,
    )

    assert not response["errors"]
    assert response["data"].get("hello") == "<b>test1</b>"
    assert "&lt;b&gt;test1&lt;/b&gt;" in response["dom"]


def test_safe_html_entities_not_encoded(client):
    data = {"hello": "test"}
    action_queue = [
        {
            "payload": {"name": "hello", "value": "<b>test1</b>"},
            "type": "syncInput",
        }
    ]
    response = post_and_get_response(
        client,
        url="/message/tests.views.test_process_component_request.FakeComponentSafe",
        data=data,
        action_queue=action_queue,
    )

    assert not response["errors"]
    assert response["data"].get("hello") == "<b>test1</b>"
    assert "<b>test1</b>" in response["dom"]
