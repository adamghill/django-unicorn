from django.conf import settings


def pytest_configure():
    templates = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["tests"],
        }
    ]
    databases = {"default": {"ENGINE": "django.db.backends.sqlite3",}}

    installed_apps = [
        "example.coffee",
    ]

    settings.configure(
        TEMPLATES=templates,
        ROOT_URLCONF="django_unicorn.urls",
        DATABASES=databases,
        INSTALLED_APPS=installed_apps,
        UNIT_TEST=True,
    )
