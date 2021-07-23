from django_unicorn.components import UnicornView


class VeryFarButtonView(UnicornView):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required

    def add_flavor(self):
        self.parent.add_flavor()
