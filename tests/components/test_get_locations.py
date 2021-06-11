import pytest

from django_unicorn.components.unicorn_view import get_locations


def test_get_locations_kebab_case():
    expected = [("HelloWorldView", "unicorn.components.hello_world")]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_with_slashes():
    expected = [("TableView", "unicorn.components.nested.table")]
    actual = get_locations("nested/table")

    assert expected == actual


def test_get_locations_with_dots():
    expected = [("table", "nested"), ("TableView", "unicorn.components.nested.table")]
    actual = get_locations("nested.table")

    assert expected == actual


def test_get_locations_fully_qualified_with_dots():
    expected = [
        ("HelloWorldView", "project.components.hello_world"),
    ]
    actual = get_locations("project.components.hello_world.HelloWorldView")
    print(actual)

    assert expected == actual


def test_get_locations_fully_qualified_with_slashes():
    expected = [
        ("HelloWorldView", "project.components.hello_world"),
    ]
    actual = get_locations("project/components/hello_world.HelloWorldView")

    assert expected == actual


def test_get_locations_fully_qualified_with_dots_ends_in_component():
    expected = [
        ("HelloWorldComponent", "project.components.hello_world"),
    ]
    actual = get_locations("project.components.hello_world.HelloWorldComponent")

    assert expected == actual


def test_get_locations_fully_qualified_with_dots_does_not_end_in_view():
    """
    The second entry in here is a mess.
    """
    expected = [
        ("HelloWorldThing", "project.components.hello_world"),
        (
            "HelloworldthingView",
            "unicorn.components.project.components.hello_world.HelloWorldThing",
        ),
    ]
    actual = get_locations("project.components.hello_world.HelloWorldThing")

    assert expected == actual


def test_get_locations_apps_setting_tuple(settings):
    settings.UNICORN["APPS"] = ("project",)

    expected = [
        ("HelloWorldView", "project.components.hello_world"),
    ]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_apps_setting_list(settings):
    settings.UNICORN["APPS"] = [
        "project",
    ]

    expected = [
        ("HelloWorldView", "project.components.hello_world"),
    ]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_apps_setting_set(settings):
    settings.UNICORN["APPS"] = {
        "project",
    }

    expected = [
        ("HelloWorldView", "project.components.hello_world"),
    ]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_apps_setting_invalid(settings):
    settings.UNICORN["APPS"] = "project"

    with pytest.raises(AssertionError) as e:
        get_locations("hello-world")

    assert e.type == AssertionError
    settings.UNICORN["APPS"] = ("unicorn",)


def test_get_locations_installed_app_with_app_config(settings):
    unicorn_apps = settings.UNICORN["APPS"]
    del settings.UNICORN["APPS"]
    settings.INSTALLED_APPS = ("example.coffee.apps.Config",)

    expected = [("HelloWorldView", "example.coffee.components.hello_world",)]
    actual = get_locations("hello-world")

    assert expected == actual
    settings.UNICORN["APPS"] = unicorn_apps

