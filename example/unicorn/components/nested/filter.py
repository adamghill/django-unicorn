from django_unicorn.components import UnicornView


class FilterView(UnicornView):
    def filter(self, name):
        return self.parent.rows.filter(lambda n: name == n)
