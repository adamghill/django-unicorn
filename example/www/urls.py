from django.urls import path
from . import views

app_name = "www"

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:name>", views.template, name="template"),
    # path("", views.FlavorListView.as_view(), name="add-flavor")
]
