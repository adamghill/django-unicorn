from tests.views.message.utils import post_and_get_response


def test_message_nested_sync_input(client):
    data = {"dictionary": {"name": "test"}}
    action_queue = [
        {
            "payload": {"name": "dictionary.name", "value": "test1"},
            "type": "syncInput",
        }
    ]
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeComponent",
        data=data,
        action_queue=action_queue,
    )

    assert not response["errors"]
    assert response["data"].get("dictionary") == {"name": "test1"}


def test_message_sync_input_choices_with_select_widget(client):
    """
    ModelForms with a Model that have a field with `choices` and the form's field uses a Select widget.
    Need to handle Select widget specifically otherwise `field.widget.format_value` will return a list
    that only contains one object.
    """

    data = {"type": 1}
    action_queue = [
        {
            "payload": {"name": "type", "value": 2},
            "type": "syncInput",
        }
    ]
    response = post_and_get_response(
        client,
        url="/message/tests.views.fake_components.FakeModelFormComponent",
        data=data,
        action_queue=action_queue,
    )

    assert not response["errors"]
    assert response["data"].get("type") == 2
