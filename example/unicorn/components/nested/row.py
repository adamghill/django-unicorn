from django_unicorn.components import UnicornView


class RowView(UnicornView):
    name = ""
    label = ""

    def save(self):
        self.name = ""
        self.label = ""
