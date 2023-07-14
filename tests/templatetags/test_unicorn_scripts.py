from django_unicorn.templatetags.unicorn import unicorn_scripts


def test_unicorn_scripts():
    actual = unicorn_scripts()

    assert actual["CSRF_HEADER_NAME"] == "X-CSRFTOKEN"
    assert actual["CSRF_COOKIE_NAME"] == "csrftoken"
    assert actual["MINIFIED"] is True


def test_unicorn_scripts_debug(settings):
    settings.DEBUG = True
    actual = unicorn_scripts()

    assert actual["CSRF_HEADER_NAME"] == "X-CSRFTOKEN"
    assert actual["CSRF_COOKIE_NAME"] == "csrftoken"
    assert actual["MINIFIED"] is False


def test_unicorn_scripts_minified_true(settings):
    settings.UNICORN = {"MINIFIED": True}
    actual = unicorn_scripts()

    assert actual["CSRF_HEADER_NAME"] == "X-CSRFTOKEN"
    assert actual["CSRF_COOKIE_NAME"] == "csrftoken"
    assert actual["MINIFIED"] is True


def test_unicorn_scripts_minified_false(settings):
    settings.UNICORN = {"MINIFIED": False}
    actual = unicorn_scripts()

    assert actual["MINIFIED"] is False


def test_unicorn_scripts_csrf_header_name(settings):
    settings.CSRF_HEADER_NAME = "HTTP_X_UNICORN"
    actual = unicorn_scripts()

    assert actual["CSRF_HEADER_NAME"] == "X-UNICORN"


def test_unicorn_scripts_csrf_cookie_name(settings):
    settings.CSRF_COOKIE_NAME = "unicorn-csrftoken"
    actual = unicorn_scripts()

    assert actual["CSRF_COOKIE_NAME"] == "unicorn-csrftoken"
