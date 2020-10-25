from django.contrib import admin
from django.urls import include, path

from unicorn.components.hello_world import HelloWorldView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("www.urls")),
    # Include django-unicorn urls
    path("unicorn/", include("django_unicorn.urls")),
    path("test", HelloWorldView.as_view(), name="test"),
]
