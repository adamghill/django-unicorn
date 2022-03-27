from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django_unicorn.components import UnicornView


class ExampleForm(forms.Form):
    like_website = forms.TypedChoiceField(
        label="Do you like this website?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial="1",
        required=True,
    )

    favorite_food = forms.CharField(
        label="What is your favorite food?",
        max_length=80,
        required=True,
    )

    favorite_color = forms.CharField(
        label="What is your favorite color?",
        max_length=80,
        required=True,
    )

    favorite_number = forms.IntegerField(
        label="Favorite number",
        required=False,
    )

    notes = forms.CharField(
        label="Additional notes or feedback",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "submit_survey"

        self.helper.add_input(Submit("submit", "Submit"))


class UnicornFormMixin:
    # form_class: forms.Form = None

    class Meta:
        javascript_exclude = ("form",)

    def __init__(self, **kwargs):
        # print("l", self.form)
        # print("m", self.get_form())

        self.form = self.get_form()

        for field_name, field in self.form.fields.items():
            # set the classes Unicorn attrs dynamically
            setattr(self.__class__, field_name, "")
            field.widget.attrs["unicorn:model.lazy"] = field_name

        super().__init__(**kwargs)


class CrispyView(UnicornFormMixin, UnicornView):
    like_website = False
    favorite_food = "Blueberries"

    form_class = ExampleForm
