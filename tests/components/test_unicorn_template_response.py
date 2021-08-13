import pytest
from bs4 import BeautifulSoup

from django_unicorn.components.unicorn_template_response import get_root_element


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

    with pytest.raises(Exception):
        actual = get_root_element(soup)

        assert str(actual) == expected
