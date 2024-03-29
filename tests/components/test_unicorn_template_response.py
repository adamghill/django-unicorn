import pytest
from bs4 import BeautifulSoup

from django_unicorn.components.unicorn_template_response import (
    UnicornTemplateResponse,
    assert_has_single_wrapper_element,
    get_root_element,
)
from django_unicorn.errors import (
    MissingComponentElementError,
    MissingComponentViewElementError,
    MultipleRootComponentElementError,
    NoRootComponentElementError,
)


def test_get_root_element():
    expected = "<div>test</div>"

    component_html = "<div>test</div>"
    soup = BeautifulSoup(component_html, features="html.parser")
    actual = get_root_element(soup)

    assert str(actual) == expected


def test_get_root_element_with_comment():
    expected = "<div>test</div>"

    component_html = "<!-- some comment --><div>test</div>"
    soup = BeautifulSoup(component_html, features="html.parser")
    actual = get_root_element(soup)

    assert str(actual) == expected


def test_get_root_element_with_blank_string():
    expected = "<div>test</div>"

    component_html = "\n<div>test</div>"
    soup = BeautifulSoup(component_html, features="html.parser")
    actual = get_root_element(soup)

    assert str(actual) == expected


def test_get_root_element_no_element():
    expected = "<div>test</div>"

    component_html = "\n"
    soup = BeautifulSoup(component_html, features="html.parser")

    with pytest.raises(MissingComponentElementError):
        actual = get_root_element(soup)

        assert str(actual) == expected


def test_get_root_element_direct_view_unicorn():
    # Annoyingly beautifulsoup adds a blank string on the attribute
    expected = '<div unicorn:view="">test</div>'

    component_html = "<html><head></head>≤body><div unicorn:view>test</div></body></html>"
    soup = BeautifulSoup(component_html, features="html.parser")
    actual = get_root_element(soup)

    assert str(actual) == expected


def test_get_root_element_direct_view_u():
    # Annoyingly beautifulsoup adds a blank string on the attribute
    expected = '<div u:view="">test</div>'

    component_html = "<html><head></head>≤body><div u:view>test</div></body></html>"
    soup = BeautifulSoup(component_html, features="html.parser")
    actual = get_root_element(soup)

    assert str(actual) == expected


def test_get_root_element_as_direct_view_unicorn():
    # Annoyingly beautifulsoup adds a blank string on the attribute
    expected = '<div unicorn:view="">test</div>'

    component_html = "<div unicorn:view>test</div>"
    soup = BeautifulSoup(component_html, features="html.parser")
    actual = get_root_element(soup)

    assert str(actual) == expected


def test_get_root_element_as_direct_view_u():
    # Annoyingly beautifulsoup adds a blank string on the attribute
    expected = '<div u:view="">test</div>'

    component_html = "<div u:view>test</div>"
    soup = BeautifulSoup(component_html, features="html.parser")
    actual = get_root_element(soup)

    assert str(actual) == expected


def test_get_root_element_direct_view_no_view():
    component_html = "<html><head></head>≤body><div>test</div></body></html>"
    soup = BeautifulSoup(component_html, features="html.parser")

    with pytest.raises(MissingComponentViewElementError):
        get_root_element(soup)


def test_desoupify():
    html = "<div>&lt;a&gt;&lt;style&gt;@keyframes x{}&lt;/style&gt;&lt;a style=&quot;animation-name:x&quot; onanimationend=&quot;alert(1)&quot;&gt;&lt;/a&gt;!\n</div>\n\n<script type=\"application/javascript\">\n  window.addEventListener('DOMContentLoaded', (event) => {\n    Unicorn.addEventListener('updated', (component) => console.log('got updated', component));\n  });\n</script>"  # noqa: E501
    expected = "<div>&lt;a&gt;&lt;style&gt;@keyframes x{}&lt;/style&gt;&lt;a style=\"animation-name:x\" onanimationend=\"alert(1)\"&gt;&lt;/a&gt;!\n</div>\n<script type=\"application/javascript\">\n  window.addEventListener('DOMContentLoaded', (event) => {\n    Unicorn.addEventListener('updated', (component) => console.log('got updated', component));\n  });\n</script>"  # noqa: E501

    soup = BeautifulSoup(html, "html.parser")

    actual = UnicornTemplateResponse._desoupify(soup)

    assert expected == actual


def test_assert_has_single_wrapper_element_one_element_no_children():
    html = '<input unicorn:model="name"></input>'
    soup = BeautifulSoup(html, "html.parser")
    root_element = get_root_element(soup)

    with pytest.raises(NoRootComponentElementError):
        assert_has_single_wrapper_element(root_element, "test-component-name")


def test_assert_has_single_wrapper_element_no_parent():
    html = """<div>
    <input unicorn:model="name1"></input>
</div>
<input unicorn:model="name2"></input>"""

    soup = BeautifulSoup(html, "html.parser")
    root_element = get_root_element(soup)

    with pytest.raises(MultipleRootComponentElementError):
        assert_has_single_wrapper_element(root_element, "test-component-name")


def test_assert_has_single_wrapper_element_true():
    html = '<div><input unicorn:model="name"></input></div>'
    soup = BeautifulSoup(html, "html.parser")
    root_element = get_root_element(soup)

    assert_has_single_wrapper_element(root_element, "test-component-name")
