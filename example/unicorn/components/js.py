from django.utils.timezone import now

from django_unicorn.components import UnicornView

from ..forms import DocumentForm


class JsView(UnicornView):
    form_class = DocumentForm

    document = ""

    states = (
        "Alabama",
        "Alaska",
        "Wisconsin",
        "Wyoming",
    )
    selected_state = ""
    select2_datetime = now()

    def call_javascript(self):
        self.call("callAlert", "world")

    def get_now(self):
        self.select2_datetime = now()

    def change_states(self):
        self.states = ("Pennsylvania",)

    def select_state(self, val, idx):
        print("select_state called", val)
        print("select_state called idx", idx)
        self.selected_state = val

    def upload_file(self):
        print("UPLOAD")

    class Meta:
        javascript_excludes = ("states",)
