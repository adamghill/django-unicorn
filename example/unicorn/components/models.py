from django_unicorn.components import UnicornView
from django_unicorn.typing import QuerySetType
from typing import Optional, cast, Any

from example.coffee.models import Flavor, Taste


class ModelsView(UnicornView):
    flavor: Optional[Flavor] = None
    flavors: QuerySetType[Flavor] = cast(QuerySetType[Flavor], Flavor.objects.none())

    def mount(self):
        self.flavor = Flavor()
        self.refresh_flavors()

    def refresh_flavors(self):
        self.flavors = cast(QuerySetType[Flavor], Flavor.objects.all().order_by("-id")[:2])

    def save_flavor(self):
        if self.flavor:
            self.flavor.save()
        self.flavor = Flavor()
        self.refresh_flavors()

    def save(self, flavor_idx: int):
        flavor_data = self.flavors[flavor_idx]
        flavor_data.save()

    def delete(self, flavor_to_delete: Flavor):
        flavor_to_delete.delete()
        self.refresh_flavors()

    def available_flavors(self):
        return Flavor.objects.all()

    def available_tastes(self):
        return Taste.objects.all()

    def model_typehint(self, flavor: Flavor):
        print(flavor)

    class Meta:
        javascript_exclude = ("flavor.taste_set",)
