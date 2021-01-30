from django_unicorn.settings import get_cache_alias, get_serial_enabled, get_settings


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
    settings.CACHES["unicorn_cache"][
        "BACKEND"
    ] = "django.core.cache.backends.dummy.DummyCache"
    settings.UNICORN["CACHE_ALIAS"] = "unicorn_cache"
    assert get_serial_enabled() is False
