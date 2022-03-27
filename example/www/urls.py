from django.urls import path

from example.unicorn.components.crispy import CrispyView
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
    path(
        "crispy-direct-view",
        CrispyView.as_view(template_name="unicorn/crispy-direct-view.html"),
        name="crispy",
    ),
    path("<str:name>", views.template, name="template"),
]
