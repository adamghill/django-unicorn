from django.utils.timezone import now

from django_unicorn.components import QuerySetType, UnicornView
from example.coffee.models import Flavor


class JsView(UnicornView):
    states = (
        "Alabama",
        "Alaska",
        "Wisconsin",
        "Wyoming",
    )
    selected_state = ""
    select2_datetime = now()
    scroll_counter = 0
    flavors: QuerySetType[Flavor] = Flavor.objects.none()
    limit = 5

    def mount(self):
        self.set_flavors()

    def call_javascript(self):
        self.call("callAlert", "world")

    def call_javascript_module(self):
        self.call("HelloJs.hello", "world!")

    def get_now(self):
        self.select2_datetime = now()

    def change_states(self):
        self.states = ("Pennsylvania",)

    def select_state(self, val, idx):
        print("select_state called", val)
        print("select_state called idx", idx)
        self.selected_state = val

    def increase_counter(self):
        self.scroll_counter += 1

    def set_flavors(self):
        self.flavors = Flavor.objects.all()[: self.limit]

    def load_more_flavors(self):
        self.limit += 5
        self.set_flavors()

    class Meta:
        javascript_excludes = ("states",)
