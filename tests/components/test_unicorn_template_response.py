import pytest

from django_unicorn.components.unicorn_template_response import (
    assert_has_single_wrapper_element,
    get_root_element,
)
from django_unicorn.errors import (
    MissingComponentElementError,
    MissingComponentViewElementError,
    MultipleRootComponentElementError,
    NoRootComponentElementError,
)
from django_unicorn.utils import html_element_to_string


def test_get_root_element():
    expected = "<div>test</div>"
    component_html = "<div>test</div>"
    actual = get_root_element(component_html)
    assert html_element_to_string(actual) == expected


def test_get_root_element_with_comment():
    expected = "<div>test</div>"
    component_html = "<!-- some comment --><div>test</div>"
    actual = get_root_element(component_html)
    assert html_element_to_string(actual) == expected


def test_get_root_element_with_blank_string():
    expected = "<div>test</div>"
    component_html = "\n<div>test</div>"
    actual = get_root_element(component_html)
    assert html_element_to_string(actual) == expected


def test_get_root_element_no_element():
    component_html = "\n"
    with pytest.raises(MissingComponentElementError):
        get_root_element(component_html)


def test_get_root_element_direct_view_unicorn():
    # lxml serializes empty attributes as just the attribute name
    expected = "<div unicorn:view>test</div>"
    component_html = "<html><head></head><body><div unicorn:view>test</div></body></html>"
    actual = get_root_element(component_html)
    assert html_element_to_string(actual) == expected


def test_get_root_element_direct_view_u():
    # lxml serializes empty attributes as just the attribute name
    expected = "<div u:view>test</div>"
    component_html = "<html><head></head><body><div u:view>test</div></body></html>"
    actual = get_root_element(component_html)
    assert html_element_to_string(actual) == expected


def test_get_root_element_as_direct_view_unicorn():
    expected = "<div unicorn:view>test</div>"
    component_html = "<div unicorn:view>test</div>"
    actual = get_root_element(component_html)
    assert html_element_to_string(actual) == expected


def test_get_root_element_as_direct_view_u():
    expected = "<div u:view>test</div>"
    component_html = "<div u:view>test</div>"
    actual = get_root_element(component_html)
    assert html_element_to_string(actual) == expected


def test_get_root_element_direct_view_no_view():
    component_html = "<html><head></head><body><div>test</div></body></html>"
    with pytest.raises(MissingComponentViewElementError):
        get_root_element(component_html)


def test_assert_has_single_wrapper_element_one_element_no_children():
    html_content = '<input unicorn:model="name">'
    with pytest.raises(NoRootComponentElementError):
        assert_has_single_wrapper_element(html_content, "test-component-name")


def test_assert_has_single_wrapper_element_multiple_roots():
    html_content = """<div>
    <input unicorn:model="name1">
</div>
<input unicorn:model="name2">"""

    with pytest.raises(MultipleRootComponentElementError):
        assert_has_single_wrapper_element(html_content, "test-component-name")


def test_assert_has_single_wrapper_element_true():
    html_content = '<div><input unicorn:model="name"></div>'
    assert_has_single_wrapper_element(html_content, "test-component-name")
