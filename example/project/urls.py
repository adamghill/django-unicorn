from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("www.urls")),
    # Include django-unicorn urls
    path("unicorn/", include("django_unicorn.urls")),
]
