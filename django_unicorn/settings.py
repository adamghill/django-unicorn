from django.conf import settings


SETTINGS_KEY = "DJANGO_UNICORN"


def get_settings():
    django_unicorn_settings = {}

    if hasattr(settings, SETTINGS_KEY):
        django_unicorn_settings = getattr(settings, SETTINGS_KEY)

    return django_unicorn_settings


def get_setting(key, default=None):
    django_unicorn_settings = get_settings()

    return django_unicorn_settings.get(key, default)
