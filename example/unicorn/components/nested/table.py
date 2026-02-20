from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class TableView(UnicornView):
    name = "Coffee Flavors"
    original_name = None
    flavors = Flavor.objects.none()
    is_editing = False
    favorite_count = 0
    show_filter = False

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
        self.flavors = Flavor.objects.select_related("favorite").all()[10:20]
        self.favorite_count = sum([1 for f in self.flavors if hasattr(f, "favorite") and f.favorite.is_favorite])

        def set_unedit(c):
            if hasattr(c, "is_editing"):
                c.is_editing = False
            for cc in c.children:
                set_unedit(cc)

        for child in self.children:
            set_unedit(child)
