from django import forms

from django_unicorn.components import UnicornView


class TodoForm(forms.Form):
    task = forms.CharField(min_length=3, max_length=10, required=True)


class TodoView(UnicornView):
    form_class = TodoForm

    task = ""
    tasks = []

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.hello = kwargs.get("hello", "not available")
        print("__init__() self.request", self.request)
        print("__init__() self.hello", self.hello)

    def hydrate(self):
        print("hydrate() self.hello", self.hello)

    def mount(self):
        print("mount() self.hello", self.hello)

    def add(self):
        print("add() self.hello", self.hello)

        if self.is_valid():
            self.tasks.append(self.task)
            self.task = ""
