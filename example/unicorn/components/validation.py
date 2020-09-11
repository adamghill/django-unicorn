from django_unicorn.components import UnicornView

from django.utils import timezone

from ..forms import ValidationForm


class ValidationView(UnicornView):
    form_class = ValidationForm

    text = "hello"
    number = ""
    now = timezone.now()

    _now_property = None

    @property
    def now_property(self):
        self._now_property = timezone.now()
        return self._now_property

    @now_property.setter
    def now_property(self, val):
        self._now_property = val

    def set_text_no_validation(self):
        self.text = "no validation"

    def set_text_with_validation(self):
        self.text = "validation"
        self.validate()
