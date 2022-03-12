from django.shortcuts import render
from django.template.loader import render_to_string

from django_unicorn.components import UnicornView
from django_unicorn.components.mixins import UnicornFormMixin
from example.unicorn.forms import ValidationForm


class SimpleFormView(UnicornFormMixin, UnicornView):
    template_name = "test_simpleform.html"
    form_class = ValidationForm

    favourite_color = "red"


# noinspection PyUnresolvedReferences
def test_form_fields_attached_as_component_attrs():
    component = SimpleFormView(component_name="test", component_id="12345678")

    assert component.text == ""
    assert component.email == ""


# def test_form_field_default(client):
#     component = SimpleFormView(component_name="test", component_id="12345678")
#
#     content = client.get("/test_forms")
#     assert content.contains("...")
