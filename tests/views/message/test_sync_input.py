import orjson

from tests.views.message.utils import post_and_get_response


def test_message_nested_sync_input(client):
    data = {"dictionary": {"name": "test"}}
    action_queue = [
        {"payload": {"name": "dictionary.name", "value": "test1"}, "type": "syncInput",}
    ]
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=action_queue,
    )

    assert not response["errors"]
    assert response["data"].get("dictionary") == {"name": "test1"}
