from django.urls import path

from example.unicorn.components.direct_view import DirectViewView

from . import views


app_name = "www"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "direct-view",
        DirectViewView.as_view(),
        name="direct-view",
    ),
    path("<str:name>", views.template, name="template"),
]
