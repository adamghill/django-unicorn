from django.shortcuts import render
from django.urls import include, path
from django.views.generic import TemplateView


def parent_view(request):
    return render(request, "templates/test_parent_template.html")


urlpatterns = (
    path("test", TemplateView.as_view(template_name="templates/test_template.html")),
    path("test-parent", parent_view, name="test-parent"),
    path(
        "test-parent-template",
        TemplateView.as_view(template_name="templates/test_parent_template.html"),
    ),
    path("", include("django_unicorn.urls")),
)
