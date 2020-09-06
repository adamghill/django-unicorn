from django_unicorn.components import UnicornView


class TextInputsView(UnicornView):
    name = "World"

    def set_name(self, name=None):
        if name:
            self.name = name
        else:
            self.name = "Universe"
