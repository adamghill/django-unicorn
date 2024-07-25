import pytest
from django.template.backends.django import Template

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
        UnicornView(component_name="test", component_id=None)

    assert e.exconly() == "AssertionError: Component id is required"


def test_init_component_id():
    component = UnicornView(component_name="test", component_id="test_init_component_id")
    assert component.component_id == "test_init_component_id"


def test_init_component_name_valid_template_name():
    component = UnicornView(component_id="test_init_component_name_valid_template_name", component_name="test")
    assert component.template_name == "unicorn/test.html"


def test_init_kebab_component_name_valid_template_name():
    component = UnicornView(
        component_id="test_init_kebab_component_name_valid_template_name", component_name="hello-world"
    )
    assert component.template_name == "unicorn/hello-world.html"


def test_init_snake_component_name_valid_template_name():
    component = UnicornView(
        component_id="test_init_snake_component_name_valid_template_name", component_name="hello_world"
    )
    assert component.template_name == "unicorn/hello_world.html"


class TemplateHtmlView(UnicornView):
    template_html = "<div>test</div>"


def test_init_template_html():
    component = TemplateHtmlView(component_id="test_init_template_html", component_name="hello_world")
    assert isinstance(component.template_name, Template)


def test_init_caches():
    component = UnicornView(component_id="test_init_caches", component_name="hello_world")
    assert len(component._methods_cache) == 0
    assert len(component._attribute_names_cache) == 0
