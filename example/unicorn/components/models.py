from typing import List

from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class ModelsView(UnicornView):
    # class attributes get stored on the class, so django-unicorn handles clearing
    # this with `_resettable_attributes_cache` in components.py
    flavor: Flavor = Flavor()
    flavors: List[Flavor] = []

    def mount(self):
        self.flavors = list(Flavor.objects.all().order_by("-id")[:2])

    def save_flavor(self):
        self.flavor.save()
        self.flavor = Flavor()

    def save(self, flavors_idx):
        flavor_data = self.flavors[flavors_idx]
        print("call save for idx", flavors_idx)
        flavor = Flavor(**flavor_data)
        flavor.save()

    def save_specific(self, flavor: Flavor):
        flavor.save()
        print("call save on flavor", flavor)
