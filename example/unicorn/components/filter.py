# -*- coding: utf-8 -*-

from django_unicorn.components import UnicornView


from typing import Any, cast


class FilterView(UnicornView):
    search = ""

    def updated_search(self, query):
        cast(Any, self.parent).load_table()

        if query:
            cast(Any, self.parent).books = list(
                filter(
                    lambda f: query.lower() in f.title.lower(),
                    cast(Any, self.parent).books,
                )
            )
            print(f"'{query}' matches {len(cast(Any, self.parent).books)} books")
