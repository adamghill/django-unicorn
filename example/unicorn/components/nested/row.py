from django_unicorn.components import UnicornView


class RowView(UnicornView):
    name = ""
    label = ""
    model = None
    is_editing = False

    def hydrate(self):
        self.name = self.model.name
        self.label = self.model.label

    def edit(self):
        print("EDIT")
        self.is_editing = True

    def save(self):
        print("SAVE!!!")
        self.name = ""
        self.label = ""
