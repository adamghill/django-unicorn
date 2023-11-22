from django.shortcuts import render
from django.urls import include, path
from django.views.generic import TemplateView

from tests.views.test_unicorn_forms import SimpleFormView

def parent_view(request):
    return render(request, "templates/test_parent_template.html")


def parent_implicit_view(request):
    return render(request, "templates/test_parent_implicit_template.html")


urlpatterns = (
    path("test", TemplateView.as_view(template_name="templates/test_template.html")),
    path("test_forms", SimpleFormView.as_view()),
    path("test-parent", parent_view, name="test-parent"),
    path("test-parent-implicit", parent_implicit_view, name="test-parent-implicit"),
    path(
        "test-parent-template",
        TemplateView.as_view(template_name="templates/test_parent_template.html"),
    ),
    path("", include("django_unicorn.urls")),
)
