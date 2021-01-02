from django_unicorn.components import UnicornView


class TableView(UnicornView):
    template_name = "unicorn/nested/table.html"
    rows = []

    def load_table(self):
        self.rows = []
