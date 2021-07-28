from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class DdtTableView(UnicornView):
    ddts = Flavor.objects.none()

    def mount(self):
        self.load_table()

    def load_table(self):
        self.ddts = Flavor.objects.all()
