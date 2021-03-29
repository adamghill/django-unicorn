from datetime import datetime
from typing import List

from django_unicorn.components import UnicornView
from django_unicorn.views.action_parsers.utils import set_property_value
from django_unicorn.views.utils import set_property_from_data


class FakeComponent(UnicornView):
    string = "property_view"
    integer = 99
    datetime = datetime(2020, 1, 1)
    array: List[str] = []


def test_set_property_from_data_str():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert "property_view" == component.string

    set_property_from_data(component, "string", "property_view_updated")

    assert "property_view_updated" == component.string


def test_set_property_value_str():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert "property_view" == component.string

    set_property_value(
        component,
        "string",
        "property_view_updated",
        {"string": "property_view_updated"},
    )

    assert "property_view_updated" == component.string


def test_set_property_from_data_int():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert 99 == component.integer

    set_property_from_data(component, "integer", 100)

    assert 100 == component.integer


def test_set_property_value_int():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert 99 == component.integer

    set_property_value(component, "integer", 100, {"integer": 100})

    assert 100 == component.integer


def test_set_property_from_data_datetime():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert datetime(2020, 1, 1) == component.datetime

    set_property_from_data(component, "datetime", datetime(2020, 1, 2))

    assert datetime(2020, 1, 2) == component.datetime


def test_set_property_from_data_list():
    """
    Prevent attempting to instantiate `List[]` type-hint doesn't throw TypeError
    """
    component = FakeComponent(component_name="test", component_id="12345678")
    assert component.array == []

    set_property_from_data(component, "array", ["string"])

    assert ["string"] == component.array


def test_set_property_value_datetime():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert datetime(2020, 1, 1) == component.datetime

    set_property_value(
        component, "datetime", datetime(2020, 1, 2), {"datetime": datetime(2020, 1, 2)}
    )

    assert datetime(2020, 1, 2) == component.datetime
