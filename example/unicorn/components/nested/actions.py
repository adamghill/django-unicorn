from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class ActionsView(UnicornView):
    model: Flavor = None
    is_editing = False

    def edit(self):
        self.is_editing = True

        # this doesn't do what you expect because resulting dom is scoped to
        # this component and the parent component won't get morphed
        self.parent.is_editing = True

    def cancel(self):
        self.is_editing = False

    def save(self):
        self.model.save()
        self.is_editing = False
