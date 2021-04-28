from django.urls import path

from example.unicorn.components.text_inputs import TextInputsView

from . import views


app_name = "www"

urlpatterns = [
    path("", views.index, name="index"),
    path("direct-view", TextInputsView.as_view(), name="direct-view",),
    path("<str:name>", views.template, name="template"),
]
