from datetime import datetime

from django_unicorn.components import UnicornField, UnicornView
from django_unicorn.views import _set_property_from_data, _set_property_from_payload


class NestedPropertyView(UnicornView):
    string = "property_view"
    integer = 99
    datetime = datetime(2020, 1, 1)


def test_set_property_from_data_str():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert "property_view" == component.string

    _set_property_from_data(component, "string", "property_view_updated")

    assert "property_view_updated" == component.string


def test_set_property_from_payload_str():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert "property_view" == component.string

    payload = {"name": "string", "value": "property_view_updated"}
    _set_property_from_payload(component, payload, {"string": "property_view_updated"})

    assert "property_view_updated" == component.string


def test_set_property_from_data_int():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert 99 == component.integer

    _set_property_from_data(component, "integer", 100)

    assert 100 == component.integer


def test_set_property_from_payload_int():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert 99 == component.integer

    payload = {"name": "integer", "value": 100}
    _set_property_from_payload(component, payload, {"integer": 100})

    assert 100 == component.integer


def test_set_property_from_data_datetime():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert datetime(2020, 1, 1) == component.datetime

    _set_property_from_data(component, "datetime", datetime(2020, 1, 2))

    assert datetime(2020, 1, 2) == component.datetime


def test_set_property_from_payload_datetime():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert datetime(2020, 1, 1) == component.datetime

    payload = {"name": "datetime", "value": datetime(2020, 1, 2)}
    _set_property_from_payload(component, payload, {"datetime": datetime(2020, 1, 2)})

    assert datetime(2020, 1, 2) == component.datetime
