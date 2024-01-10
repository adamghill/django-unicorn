from django_unicorn.components import UnicornView


class FilterView(UnicornView):
    search = ""

    def updated_search(self, query):
        self.parent.load_table()

        if query:
            self.parent.flavors = list(filter(lambda f: query.lower() in f.name.lower(), self.parent.flavors))

        self.parent.force_render = True
