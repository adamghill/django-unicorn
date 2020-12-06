from datetime import datetime

from django import forms

from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class FakeComponent(UnicornView):
    template_name = "templates/test_component.html"
    dictionary = {"name": "test"}
    method_count = 0
    check = True

    def test_method(self):
        self.method_count += 1

    def test_method_params(self, count):
        self.method_count = count


class FakeModelComponent(UnicornView):
    template_name = "templates/test_component.html"
    flavors = Flavor.objects.all()

    def hydrate(self):
        self.flavors = Flavor.objects.all()


class FakeValidationForm(forms.Form):
    text = forms.CharField(min_length=3, max_length=10)
    date_time = forms.DateTimeField()
    number = forms.IntegerField()


class FakeValidationComponent(UnicornView):
    template_name = "templates/test_component.html"
    form_class = FakeValidationForm

    text = "hello"
    number = ""
    date_time = datetime(2020, 9, 13, 17, 45, 14)

    def set_text_no_validation(self):
        self.text = "no validation"

    def set_text_with_validation(self):
        self.text = "validation 33"
        self.validate()

    def set_number(self, number):
        self.number = number
