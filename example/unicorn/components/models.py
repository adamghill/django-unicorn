from django_unicorn.components import QuerySetType, UnicornView
from example.coffee.models import Flavor


class ModelsView(UnicornView):
    flavor: Flavor = Flavor()
    flavors: QuerySetType[Flavor] = Flavor.objects.none()

    def mount(self):
        self.refresh_flavors()

    def refresh_flavors(self):
        self.flavors = Flavor.objects.all().order_by("-id")[:2]

    def save_flavor(self):
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

    class Meta:
        javascript_exclude = ("available_flavors",)
