from django_unicorn.components import UnicornField, UnicornView
from django_unicorn.views.utils import set_property_from_data


class NestedPropertyOne(UnicornField):
    name = "nested_property_one"


class PropertyOne(UnicornField):
    nested_property_one = NestedPropertyOne()
    name = "property_one"


class NestedPropertyView(UnicornView):
    property_one = PropertyOne()
    name = "property_view"


def test_set_property_from_data_unicorn_field():
    component = NestedPropertyView(component_name="test", component_id="test_set_property_from_data_unicorn_field")
    assert "property_one" == component.property_one.name

    data = {"name": "property_one_updated"}
    set_property_from_data(component, "property_one", data)

    assert "property_one_updated" == component.property_one.name


def test_set_property_from_data_nested_unicorn_field():
    component = NestedPropertyView(
        component_name="test", component_id="test_set_property_from_data_nested_unicorn_field"
    )
    assert "nested_property_one" == component.property_one.nested_property_one.name

    data = {"nested_property_one": {"name": "nested_property_one_updated"}}
    set_property_from_data(component, "property_one", data)

    assert "nested_property_one_updated" == component.property_one.nested_property_one.name
