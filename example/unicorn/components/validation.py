from django_unicorn.components import UnicornView

from django.utils import timezone

from ..forms import ValidationForm


class ValidationView(UnicornView):
    form_class = ValidationForm

    blob = "hello"
    number = ""
    now = timezone.now()
