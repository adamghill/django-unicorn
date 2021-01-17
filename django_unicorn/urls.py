from django.urls import path, re_path

from . import views


app_name = "django_unicorn"


urlpatterns = (
    re_path("message/(?P<component_name>[\w/\.-]+)", views.message, name="message"),
    path(
        "message", views.message, name="message"
    ),  # Only here to build the correct url in scripts.html
)
