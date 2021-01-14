from coffee.models import Flavor

from django_unicorn.components import UnicornView


class TableView(UnicornView):
    name = "Coffee Flavors"
    original_name = None
    flavors = Flavor.objects.none()
    is_editing = False

    def edit(self):
        self.is_editing = True
        self.original_name = self.name

    def save(self):
        self.is_editing = False

    def cancel(self):
        if self.original_name:
            self.name = self.original_name
            self.original_name = None

        self.is_editing = False

    def mount(self):
        self.load_table()

    def load_table(self):
        self.flavors = Flavor.objects.all()[10:20]

        for child in self.children:
            if hasattr(child, "is_editing"):
                child.is_editing = False
