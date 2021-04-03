from django.conf import settings

import pytest


def pytest_configure():
    templates = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["tests"],
        }
    ]
    databases = {"default": {"ENGINE": "django.db.backends.sqlite3",}}

    installed_apps = [
        "example.coffee.apps.Config",
        "example.books.apps.Config",
    ]

    unicorn_settings = {
        "SERIAL": {"ENABLED": True, "TIMEOUT": 5},
        "CACHE_ALIAS": "default",
        "APPS": ("unicorn",),
    }

    caches = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

    settings.configure(
        TEMPLATES=templates,
        ROOT_URLCONF="django_unicorn.urls",
        DATABASES=databases,
        INSTALLED_APPS=installed_apps,
        UNIT_TEST=True,
        UNICORN=unicorn_settings,
        CACHES=caches,
    )


@pytest.fixture(autouse=True)
def reset_settings(settings):
    """
    This takes the original `UNICORN` settings before the test is run, runs the test, and then resets them afterwards.
    This is required because mutating nested dictionaries does not reset them as expected by `pytest-django`.
    More details in https://github.com/pytest-dev/pytest-django/issues/601#issuecomment-440676001.
    """

    # Get original settings
    cache_settings = {**settings.CACHES}
    unicorn_settings = {**settings.UNICORN}
    django_unicorn_settings = {}

    if hasattr(settings, "DJANGO_UNICORN"):
        django_unicorn_settings = {**settings.DJANGO_UNICORN}

    # Run test
    yield

    # Re-set original settings
    settings.CACHES = cache_settings
    settings.UNICORN = unicorn_settings

    if django_unicorn_settings:
        settings.DJANGO_UNICORN = django_unicorn_settings
