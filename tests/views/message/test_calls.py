from django_unicorn.components import UnicornView
from tests.views.message.utils import post_and_get_response


class FakeCallsComponent(UnicornView):
    template_name = "templates/test_component.html"

    def test_call(self):
        self.call("testCall")

    def test_call2(self):
        self.call("testCall2")


FAKE_CALLS_COMPONENT_URL = "/message/tests.views.message.test_calls.FakeCallsComponent"


def test_message_calls(client):
    action_queue = [
        {"payload": {"name": "test_call"}, "type": "callMethod", "target": None,}
    ]

    response = post_and_get_response(
        client, url=FAKE_CALLS_COMPONENT_URL, action_queue=action_queue
    )

    body = response.json()
    assert body.get("calls") == [{"fn": "testCall"}]


def test_message_multiple_calls(client):
    action_queue = [
        {"payload": {"name": "test_call"}, "type": "callMethod", "target": None,},
        {"payload": {"name": "test_call2"}, "type": "callMethod", "target": None,},
    ]
    response = post_and_get_response(
        client, url=FAKE_CALLS_COMPONENT_URL, action_queue=action_queue
    )

    body = response.json()
    assert body.get("calls") == [{"fn": "testCall"}, {"fn": "testCall2"}]
