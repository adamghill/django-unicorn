from django.urls import path, re_path

from django_unicorn.views import UnicornMessageHandler

app_name = "django_unicorn"

urlpatterns = (
    re_path(r"message/(?P<component_name>[\w/\.-]+)", UnicornMessageHandler.as_view(), name="message"),
    path("message", UnicornMessageHandler.as_view(), name="message"),  # Only here to build the correct url in scripts.html
)
