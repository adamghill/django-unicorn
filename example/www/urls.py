from django.urls import path

from example.unicorn.components.direct_view import DirectViewView
from example.unicorn.components.redirects import RedirectsView

from . import views


app_name = "www"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "direct-view",
        DirectViewView.as_view(),
        name="direct-view",
    ),
    path(
        "redirects",
        RedirectsView.as_view(),
        name="redirects",
    ),
    path(
        "class-view",
        views.ClassViewView.as_view(),
        name="class-view",
    ),
    path("<str:name>", views.template, name="template"),
]
