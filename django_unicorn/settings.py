import logging

from django.conf import settings


logger = logging.getLogger(__name__)


SETTINGS_KEY = "UNICORN"
LEGACY_SETTINGS_KEY = f"DJANGO_{SETTINGS_KEY}"


def get_settings():
    unicorn_settings = {}

    if hasattr(settings, LEGACY_SETTINGS_KEY):
        # TODO: Log deprecation message here
        unicorn_settings = getattr(settings, LEGACY_SETTINGS_KEY)
    elif hasattr(settings, SETTINGS_KEY):
        unicorn_settings = getattr(settings, SETTINGS_KEY)

    return unicorn_settings


def get_setting(key, default=None):
    unicorn_settings = get_settings()

    return unicorn_settings.get(key, default)


def get_serial_settings():
    return get_setting("SERIAL", {})


def get_cache_alias():
    return get_setting("CACHE_ALIAS", "default")


def get_script_location():
    """
    Valid choices: "append", "after". Default is "after".
    """

    return get_setting("SCRIPT_LOCATION", "after")


def get_serial_enabled():
    """
    Default serial enabled is `False`.
    """
    enabled = get_serial_settings().get("ENABLED", False)

    if enabled and settings.CACHES:
        cache_alias = get_cache_alias()
        cache_settings = settings.CACHES.get(cache_alias, {})
        cache_backend = cache_settings.get("BACKEND")

        if cache_backend == "django.core.cache.backends.dummy.DummyCache":
            return False

    return enabled


def get_serial_timeout():
    """
    Default serial timeout is 60 seconds.
    """
    return get_serial_settings().get("TIMEOUT", 60)


def get_minify_html_enabled():
    minify_html_enabled = get_setting("MINIFY_HTML", False)

    if minify_html_enabled:
        try:
            import htmlmin
        except ModuleNotFoundError:
            logger.error(
                "MINIFY_HTML is `True`, but minify extra could not be imported. Install with `django-unicorn[minify]`."
            )

            return False

    return minify_html_enabled
