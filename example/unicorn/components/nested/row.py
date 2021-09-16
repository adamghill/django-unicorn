from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


def callback(func):
    """A decorator for callbacks passed as kwargs to a child component
    
    This allows the bound method itself to be resolved in the template.
    Without it, the template variable resolver will automatically call
    the method and use what is returned as the resolved value.
    """
    func.do_not_call_in_templates = True
    return func


class RowView(UnicornView):
    model: Flavor = None
    is_editing = False

    @callback
    def on_edit(self):
        print("on_edit callback fired")
        self.is_editing = True

    @callback
    def on_cancel(self):
        self.is_editing = False

    @callback
    def on_save(self):
        self.model.save()
        self.is_editing = False