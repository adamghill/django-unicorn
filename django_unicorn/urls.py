from django.urls import path, re_path

from . import views


app_name = "django_unicorn"


urlpatterns = (
    re_path("message/(?P<component_name>[\w/\.-]+)", views.message, name="message"),
    re_path(
        "message-async/(?P<component_name>[\w/\.-]+)",
        views.message_async,
        name="message_async",
    ),
    # Only here to build the correct url in scripts.html
    path("message", views.message, name="message"),
    path("message-async", views.message_async, name="message_async"),
)
