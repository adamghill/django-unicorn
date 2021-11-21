from django.urls import include, path
from django.views.generic import TemplateView


urlpatterns = (
    path("test", TemplateView.as_view(template_name="templates/test_template.html")),
    path("", include("django_unicorn.urls")),
)
