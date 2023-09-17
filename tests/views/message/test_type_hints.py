from dataclasses import dataclass
from decimal import Decimal

from tests.views.message.utils import post_and_get_response

from django_unicorn.components import UnicornView


@dataclass
class ExampleDataclass:
    hello: str = "world"


class FakeObjectsComponent(UnicornView):
    template_name = "templates/test_component.html"

    decimal_example: Decimal = Decimal(1.1)
    float_example: float = 1.2
    int_example: int = 3
    dataclass_example: ExampleDataclass = None

    def assert_int(self):
        assert self.int_example == 4

    def assert_float(self):
        assert self.float_example == 1.3

    def assert_decimal(self):
        assert self.decimal_example == Decimal(1.5)

    def assert_dataclass(self):
        assert self.dataclass_example == ExampleDataclass(hello="world")
        assert self.dataclass_example.hello == "world"


FAKE_OBJECTS_COMPONENT_URL = "/message/tests.views.message.test_type_hints.FakeObjectsComponent"


def test_message_int(client):
    data = {"int_example": "4"}
    action_queue = [
        {
            "payload": {"name": "assert_int"},
            "type": "callMethod",
        }
    ]
    response = post_and_get_response(
        client,
        url=FAKE_OBJECTS_COMPONENT_URL,
        data=data,
        action_queue=action_queue,
    )

    assert not response.get("error")  # UnicornViewError/AssertionError returns a a JsonResponse with "error" key
    assert not response["errors"]


def test_message_float(client):
    data = {"float_example": "1.3"}
    action_queue = [
        {
            "payload": {"name": "assert_float"},
            "type": "callMethod",
        }
    ]
    response = post_and_get_response(
        client,
        url=FAKE_OBJECTS_COMPONENT_URL,
        data=data,
        action_queue=action_queue,
    )

    assert not response.get("error")  # UnicornViewError/AssertionError returns a a JsonResponse with "error" key
    assert not response["errors"]


def test_message_decimal(client):
    data = {"decimal_example": "1.5"}
    action_queue = [
        {
            "payload": {"name": "assert_decimal"},
            "type": "callMethod",
        }
    ]
    response = post_and_get_response(
        client,
        url=FAKE_OBJECTS_COMPONENT_URL,
        data=data,
        action_queue=action_queue,
    )

    assert not response.get("error")  # UnicornViewError/AssertionError returns a a JsonResponse with "error" key
    assert not response["errors"]


def test_message_dataclass(client):
    data = {"dataclass_example": {"hello": "world"}}
    action_queue = [
        {
            "payload": {"name": "assert_dataclass"},
            "type": "callMethod",
        }
    ]
    response = post_and_get_response(
        client,
        url=FAKE_OBJECTS_COMPONENT_URL,
        data=data,
        action_queue=action_queue,
    )

    assert not response.get("error")  # UnicornViewError/AssertionError returns a a JsonResponse with "error" key
    assert not response["errors"]
