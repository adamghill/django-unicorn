from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class RowView(UnicornView):
    model: Flavor = None
    is_editing = False

    def edit(self):
        self.is_editing = True

    def cancel(self):
        self.is_editing = False

    def save(self):
        self.model.save()
        self.is_editing = False
