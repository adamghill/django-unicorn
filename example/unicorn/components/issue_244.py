from django.core.paginator import Paginator
from django.utils.translation import ugettext_lazy as _  # noqa

from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class Issue244View(UnicornView):
    items_per_page = 10
    title = ""
    page_index = 1
    paginator = None
    page = None

    class Meta:
        exclude = ()
        javascript_exclude = (
            "paginator",
            "page",
        )

    def mount(self):
        print("mount")
        self._search_documents()

    def _search_documents(self):
        print("  _search_documents")

        qs = Flavor.objects.filter()

        if self.title:
            qs = qs.filter(name__icontains=self.title)

        qs = qs.order_by("name")

        paginator = Paginator(qs, self.items_per_page)
        self.paginator = paginator
        self.page = paginator.page(self.page_index)
        return self.page

    def search_documents(self):
        print("search_documents")
        self._search_documents()

    def next_page(self):
        print("next_page")
        self.page_index += 1
        self._search_documents()

    def previous_page(self):
        print("previous_page")
        self.page_index = max(self.page_index - 1, 1)
        self._search_documents()
