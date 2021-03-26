from django_unicorn.components import UnicornView
from django_unicorn.views.utils import set_property_from_data


class DictPropertyView(UnicornView):
    dictionary = {"name": "dictionary"}
    nested_dictionary = {"nested": {"name": "nested_dictionary"}}


def test_set_property_from_data_dict():
    component = DictPropertyView(component_name="test", component_id="12345678")
    assert "dictionary" == component.dictionary.get("name")

    set_property_from_data(component, "dictionary", {"name": "dictionary_updated"})

    assert "dictionary_updated" == component.dictionary.get("name")


def test_set_property_from_data_nested_dict():
    component = DictPropertyView(component_name="test", component_id="12345678")
    assert "nested_dictionary" == component.nested_dictionary.get("nested").get("name")

    set_property_from_data(
        component,
        "nested_dictionary",
        {"nested": {"name": "nested_dictionary_updated"}},
    )

    assert "nested_dictionary_updated" == component.nested_dictionary.get("nested").get(
        "name"
    )
