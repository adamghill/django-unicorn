from datetime import datetime

from django_unicorn.components import UnicornView

from ..forms import ValidationForm


class ValidationView(UnicornView):
    form_class = ValidationForm

    text = "hello"
    number = ""
    date_time = datetime(2020, 9, 13, 17, 45, 14)
    email = ""

    def set_text_no_validation(self):
        self.text = "no validation"

    def set_text_with_validation(self):
        self.text = "validation"
        self.validate()

    def set_number(self, number):
        self.number = number
