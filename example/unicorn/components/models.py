from django_unicorn.components import UnicornView

from coffee.models import Flavor


class ModelsView(UnicornView):
    flavors = Flavor.objects.none()
    class_flavor = Flavor()

    def __init__(self, **kwargs):
        self.instance_flavor = Flavor()
        super().__init__(**kwargs)

    def hydrate(self):
        self.flavors = Flavor.objects.all().order_by("-id")[:3]

    def add_instance_flavor(self):
        self.instance_flavor.save()
        # self.instance_flavor = Flavor()
        self.reset()

    def add_class_flavor(self):
        self.class_flavor.save()
        # self.class_flavor = Flavor()
        self.reset()
