from django.urls import include, path
from django.views.generic import TemplateView

from tests.views.test_unicorn_forms import SimpleFormView

urlpatterns = (
    path("test", TemplateView.as_view(template_name="templates/test_template.html")),
    path("test_forms", SimpleFormView.as_view()),
    path("", include("django_unicorn.urls")),
)
