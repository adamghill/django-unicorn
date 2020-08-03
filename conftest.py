from django.conf import settings


def pytest_configure():
    templates = [
        {"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [],}
    ]

    settings.configure(TEMPLATES=templates, ROOT_URLCONF="django_unicorn.urls")
