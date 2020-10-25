from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class TestComponent(UnicornView):
    template_name = "templates/test_component.html"
    dictionary = {"name": "test"}
    method_count = 0

    def test_method(self):
        self.method_count += 1



class TestModelComponent(UnicornView):
    template_name = "templates/test_component.html"
    flavors = Flavor.objects.all()

    def hydrate(self):
        self.flavors = Flavor.objects.all()
