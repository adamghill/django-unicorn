from django_unicorn.views.action_parsers.call_method import _get_property_value
from tests.views.fake_components import FakeComponent


def test_get_property_value(client):
    component = FakeComponent(component_name="test", component_id="asdf")

    component.check = False
    check_value = _get_property_value(component, "check")
    assert check_value is False

    component.check = True
    check_value = _get_property_value(component, "check")

    assert check_value is True


def test_get_property_value_nested(client):
    component = FakeComponent(component_name="test", component_id="asdf")

    component.nested["check"] = False
    check_value = _get_property_value(component, "nested.check")
    assert check_value is False

    component.nested["check"] = True
    check_value = _get_property_value(component, "nested.check")

    assert check_value is True
