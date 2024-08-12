import pytest

from django_unicorn.settings import (
    get_cache_alias,
    get_minify_html_enabled,
    get_morpher_settings,
    get_script_location,
    get_serial_enabled,
)


def test_settings_cache_alias(settings):
    settings.UNICORN["CACHE_ALIAS"] = "unicorn_cache"

    expected = "unicorn_cache"
    actual = get_cache_alias()
    assert expected == actual


def test_settings_legacy(settings):
    settings.DJANGO_UNICORN = {}
    settings.DJANGO_UNICORN["CACHE_ALIAS"] = "unicorn_cache"

    expected = "unicorn_cache"
    actual = get_cache_alias()
    assert expected == actual


def test_get_serial_enabled(settings):
    settings.UNICORN["SERIAL"]["ENABLED"] = False
    assert get_serial_enabled() is False

    settings.UNICORN["SERIAL"]["ENABLED"] = True
    assert get_serial_enabled() is True

    settings.UNICORN["SERIAL"]["ENABLED"] = True
    settings.CACHES["unicorn_cache"] = {}
    settings.CACHES["unicorn_cache"]["BACKEND"] = "django.core.cache.backends.dummy.DummyCache"
    settings.UNICORN["CACHE_ALIAS"] = "unicorn_cache"
    assert get_serial_enabled() is False


def test_settings_minify_html_false(settings):
    settings.UNICORN["MINIFY_HTML"] = False

    assert get_minify_html_enabled() is False


def test_settings_minify_html_true(settings):
    settings.UNICORN["MINIFY_HTML"] = True

    assert get_minify_html_enabled() is True

    settings.UNICORN["MINIFY_HTML"] = False


def test_get_script_location(settings):
    assert get_script_location() == "after"

    settings.UNICORN["SCRIPT_LOCATION"] = "append"

    assert get_script_location() == "append"

    del settings.UNICORN["SCRIPT_LOCATION"]

    assert get_script_location() == "after"


def test_get_morpher_settings(settings):
    assert get_morpher_settings() == {"NAME": "morphdom"}

    settings.UNICORN["MORPHER"] = {"NAME": "alpine"}
    assert get_morpher_settings()["NAME"] == "alpine"

    settings.UNICORN["MORPHER"] = {"NAME": "blob"}

    with pytest.raises(AssertionError) as e:
        get_morpher_settings()

    assert e.type is AssertionError
    assert e.exconly() == "AssertionError: Unknown morpher name: blob"

    del settings.UNICORN["MORPHER"]
