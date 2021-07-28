from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class FilterView(UnicornView):
    search = ""

    def updated_search(
        self, query
    ):  # this function is not called when the search field is updated. Why?
        print("updated called?")
        self.parent.load_table()

        if query:
            self.parent.ddts = list(
                filter(lambda f: query.lower() in f.name.lower(), self.parent.ddts)
            )
