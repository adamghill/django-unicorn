from django import forms


class ValidationForm(forms.Form):
    now = forms.DateTimeField()
    now_property = forms.DateTimeField()
    number = forms.IntegerField()
