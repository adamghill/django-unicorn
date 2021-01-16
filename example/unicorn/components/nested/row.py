from django_unicorn.components import UnicornView


class RowView(UnicornView):
    model = None
    is_editing = False

    def edit(self):
        self.is_editing = True

    def cancel(self):
        self.is_editing = False

    def save(self):
        self.model.save()
        self.is_editing = False
