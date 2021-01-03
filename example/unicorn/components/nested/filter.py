from django_unicorn.components import UnicornView


class FilterView(UnicornView):
    search = ""

    def updated_search(self, query):
        try:
            self.parent.load_table()

            if query:
                print("query", query)
                self.parent.flavors = list(
                    filter(
                        lambda f: query.lower() in f.name.lower(), self.parent.flavors
                    )
                )
                print("self.parent.flavors", self.parent.flavors)
        except Exception as e:
            print("e", e)
