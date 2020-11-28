import pytest

from django_unicorn.components import UnicornView


def test_init_no_component_name():
    with pytest.raises(AssertionError) as e:
        UnicornView()

    assert e.exconly() == "AssertionError: Component name is required"


def test_init_no_component_id():
    with pytest.raises(AssertionError) as e:
        UnicornView(component_name="test")

    assert e.exconly() == "AssertionError: Component id is required"


def test_init_none_component_id():
    with pytest.raises(AssertionError) as e:
        component = UnicornView(component_name="test", component_id=None)

    assert e.exconly() == "AssertionError: Component id is required"


def test_init_component_id():
    component = UnicornView(component_name="test", component_id="12345678")
    assert component.component_id == "12345678"
    assert len(component.component_id) == 8


def test_init_component_name_valid_template_name():
    component = UnicornView(component_id="asdf1234", component_name="test")
    assert component.template_name == "unicorn/test.html"


def test_init_kebab_component_name_valid_template_name():
    component = UnicornView(component_id="asdf1234", component_name="hello-world")
    assert component.template_name == "unicorn/hello-world.html"


def test_init_snake_component_name_valid_template_name():
    component = UnicornView(component_id="asdf1234", component_name="hello_world")
    assert component.template_name == "unicorn/hello_world.html"


def test_init_caches():
    component = UnicornView(component_id="asdf1234", component_name="hello_world")
    assert len(component._methods_cache) == 0
    assert len(component._attribute_names_cache) == 0
