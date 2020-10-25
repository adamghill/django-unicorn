from django_unicorn.components import UnicornField, UnicornView
from django_unicorn.views import _set_property_from_data, _set_property_from_payload


class NestedPropertyOne(UnicornField):
    name = "nested_property_one"


class PropertyOne(UnicornField):
    nested_property_one = NestedPropertyOne()
    name = "property_one"


class NestedPropertyView(UnicornView):
    property_one = PropertyOne()
    name = "property_view"


def test_set_property_from_data_unicorn_field():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert "property_one" == component.property_one.name

    data = {"name": "property_one_updated"}
    _set_property_from_data(component, "property_one", data)

    assert "property_one_updated" == component.property_one.name


def test_set_property_from_data_nested_unicorn_field():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert "nested_property_one" == component.property_one.nested_property_one.name

    data = {"nested_property_one": {"name": "nested_property_one_updated"}}
    _set_property_from_data(component, "property_one", data)

    assert (
        "nested_property_one_updated" == component.property_one.nested_property_one.name
    )
