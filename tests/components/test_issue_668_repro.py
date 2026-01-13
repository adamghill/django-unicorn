
import pytest
from bs4 import BeautifulSoup
from django_unicorn.components.unicorn_template_response import (
    assert_has_single_wrapper_element,
    get_root_element,
)
from django_unicorn.errors import MultipleRootComponentElementError

def test_issue_668_unicorn_view_and_poll():
    # User reported case
    html = '<div unicorn:view unicorn:poll="get_updates">Content</div>'
    soup = BeautifulSoup(html, "html.parser")
    root_element = get_root_element(soup)

    # This should NOT rasie MultipleRootComponentElementError
    try:
        assert_has_single_wrapper_element(root_element, "test-component")
    except MultipleRootComponentElementError:
        pytest.fail("MultipleRootComponentElementError raised incorrectly for unicorn:view + unicorn:poll")

def test_issue_668_unicorn_view_no_poll():
    # Control case
    html = '<div unicorn:view>Content</div>'
    soup = BeautifulSoup(html, "html.parser")
    root_element = get_root_element(soup)

    assert_has_single_wrapper_element(root_element, "test-component")
