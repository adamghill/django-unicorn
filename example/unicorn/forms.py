from django import forms


class ValidationForm(forms.Form):
    now = forms.DateTimeField()
    number = forms.IntegerField()
