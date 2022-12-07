from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class AccountSearchView(UnicornView):
    id_search_term = ""
    name_search_term = ""
    description_search_term = ""

    current_page = 1
    next_page = None
    previous_page = None
    first_page = None
    last_page = None

    def go_to_page(self, page_number):
        self.current_page = page_number
        self.accounts()

    def accounts(self):
        print(self.id_search_term)
        accounts = Flavor.objects.filter(id__icontains=self.id_search_term).filter(
            name__icontains=self.name_search_term
        )

        paginator = Paginator(accounts, 50)

        try:
            page = paginator.page(self.current_page)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page = paginator.page(self.current_page)
        except EmptyPage:
            # if the page is out of range, deliver the last pa
            page = paginator.page(paginator.num_pages)

        self.last_page = int(
            paginator.num_pages
        )  # as soon i add this line the component breaks

        return page
