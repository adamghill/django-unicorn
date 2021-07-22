from django.core.paginator import Paginator
from django.utils.translation import ugettext_lazy as _  # noqa

from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class Issue244View(UnicornView):
    first_load = True
    items_per_page = 10
    title = ""
    page_index = 1
    paginator = None
    page = None

    class Meta:
        exclude = ()
        javascript_exclude = ("paginator", "page", "http_request", "_search_documents")

    def mount(self):
        print("mount")
        self._search_documents()

    def hydrate(self):
        print("hydrate first_load", self.first_load)
        if self.first_load is True:
            self._search_documents()

        self.first_load = False

    def _search_documents(self):
        qs = Flavor.objects.filter()

        if self.title:
            qs = qs.filter(name__icontains=self.title)

        paginator = Paginator(qs, self.items_per_page)
        self.paginator = paginator
        self.page = paginator.page(self.page_index)
        return self.page

    def search_documents(self):
        self._search_documents()

    def next_page(self):
        self.page_index += 1
        self._search_documents()

    def previous_page(self):
        self.page_index = max(self.page_index - 1, 1)
        self._search_documents()
