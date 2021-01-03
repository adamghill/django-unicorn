from coffee.models import Flavor

from django_unicorn.components import UnicornView


class TableView(UnicornView):
    name = "Coffee Flavors"
    flavors = Flavor.objects.none()
    is_editing = False

    def edit(self):
        self.is_editing = True

    def save(self):
        self.is_editing = False

    def hydrate(self):
        self.load_table()

    def load_table(self):
        self.flavors = Flavor.objects.all()[10:20]
