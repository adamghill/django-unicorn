from django.urls import path

from . import views


app_name = "django_unicorn"


urlpatterns = (
    path("message/<str:component_name>", views.message, name="message"),
    path(
        "message", views.message, name="message"
    ),  # Only here to build the correct url in scripts.html
)
