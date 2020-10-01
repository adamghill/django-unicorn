from django_unicorn.components import UnicornView

from coffee.models import Flavor


class ModelsView(UnicornView):
    flavors = Flavor.objects.all()
    flavor = Flavor.objects.filter(id=1).first()

    def save(self):
        self.flavor.save()
