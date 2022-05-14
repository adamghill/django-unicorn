from django.urls import path

from example.unicorn.components.direct_view import DirectViewView
from example.unicorn.components.issue_397 import Issue397View

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
        "issue-397",
        Issue397View.as_view(),
        name="issue-397",
    ),
    path("<str:name>", views.template, name="template"),
]
