from django_unicorn.components import UnicornView


class TableView(UnicornView):
    rows = []

    def load_table(self):
        self.rows = []
