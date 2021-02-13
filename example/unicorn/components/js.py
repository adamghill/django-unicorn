from django_unicorn.components import UnicornView


class JsView(UnicornView):
    def mount(self):
        # self.call("callAlert")
        pass

    def call_javascript(self):
        self.call("callAlert", "world")

    def choose_state():
        pass

    states = (
        "Alabama",
        "Alaska",
        "Wisconsin",
        "Wyoming",
    )

    class Meta:
        javascript_excludes = ("states",)
