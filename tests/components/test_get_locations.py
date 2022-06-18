import pytest

from django_unicorn.components.unicorn_view import get_locations


@pytest.fixture
def cache_clear():
    get_locations.cache_clear()


@pytest.fixture
def clear_apps(settings):
    unicorn_apps = settings.UNICORN["APPS"]
    del settings.UNICORN["APPS"]

    yield

    settings.UNICORN["APPS"] = unicorn_apps


def test_get_locations_kebab_case(cache_clear):
    expected = [("unicorn.components.hello_world", "HelloWorldView")]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_with_slashes(cache_clear):
    expected = [("unicorn.components.nested.table", "TableView")]
    actual = get_locations("nested/table")

    assert expected == actual


def test_get_locations_with_dots(cache_clear):
    expected = [("nested", "table"), ("unicorn.components.nested.table", "TableView")]
    actual = get_locations("nested.table")

    assert expected == actual


def test_get_locations_fully_qualified_with_dots(cache_clear):
    expected = [
        ("project.components.hello_world", "HelloWorldView"),
    ]
    actual = get_locations("project.components.hello_world.HelloWorldView")

    assert expected == actual


def test_get_locations_fully_qualified_with_slashes(cache_clear):
    expected = [
        ("project.components.hello_world", "HelloWorldView"),
    ]
    actual = get_locations("project/components/hello_world.HelloWorldView")

    assert expected == actual


def test_get_locations_fully_qualified_with_dots_ends_in_component(cache_clear):
    expected = [
        ("project.components.hello_world", "HelloWorldComponent"),
    ]
    actual = get_locations("project.components.hello_world.HelloWorldComponent")

    assert expected == actual


def test_get_locations_fully_qualified_with_dots_does_not_end_in_view(cache_clear):
    """
    The second entry in here is a mess.
    """

    expected = [
        ("project.components.hello_world", "HelloWorldThing"),
        (
            "unicorn.components.project.components.hello_world.HelloWorldThing",
            "HelloworldthingView",
        ),
    ]
    actual = get_locations("project.components.hello_world.HelloWorldThing")

    assert expected == actual


def test_get_locations_apps_setting_tuple(settings, cache_clear):
    settings.UNICORN["APPS"] = ("project",)

    expected = [
        ("project.components.hello_world", "HelloWorldView"),
    ]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_apps_setting_list(settings, cache_clear):
    settings.UNICORN["APPS"] = [
        "project",
    ]

    expected = [
        ("project.components.hello_world", "HelloWorldView"),
    ]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_apps_setting_set(settings, cache_clear):
    settings.UNICORN["APPS"] = {
        "project",
    }

    expected = [
        ("project.components.hello_world", "HelloWorldView"),
    ]
    actual = get_locations("hello-world")

    assert expected == actual


def test_get_locations_apps_setting_invalid(settings, cache_clear):
    settings.UNICORN["APPS"] = "project"

    with pytest.raises(AssertionError) as e:
        get_locations("hello-world")

    assert e.type == AssertionError
    settings.UNICORN["APPS"] = ("unicorn",)


def test_get_locations_installed_app_with_app_config(settings, clear_apps, cache_clear):
    settings.INSTALLED_APPS = [
        "example.coffee.apps.Config",
    ]

    expected = [("example.coffee.components.hello_world", "HelloWorldView")]
    actual = get_locations("hello-world")

    assert expected == actual

    # test when the app is in a subdirectory "apps" with Config
    settings.INSTALLED_APPS[0] = "foo_project.apps.bar_app.apps.Config"
    expected_location = [("foo_project.apps.bar_app.components.foo_bar", "FooBarView")]
    actual_location = get_locations("foo-bar")
    assert expected_location == actual_location


def test_get_locations_installed_app_with_apps(settings, clear_apps, cache_clear):
    # test when the app is in a subdirectory "apps"
    settings.INSTALLED_APPS = ["example.apps.main",]
    expected_location = [("example.apps.main.components.sidebar_menu", "SidebarMenuView")]
    actual_location = get_locations("sidebar-menu")
    assert expected_location == actual_location
