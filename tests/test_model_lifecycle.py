import pytest

from django_unicorn.components import UnicornView
from django_unicorn.serializer import dumps, loads
from django_unicorn.typer import _construct_model
from django_unicorn.views.utils import set_property_from_data
from example.coffee.models import Flavor


class FakeComponent(UnicornView):
    flavors = Flavor.objects.none()

    def __init__(self, **kwargs):
        self.flavors = Flavor.objects.none()
        super().__init__(**kwargs)


@pytest.mark.django_db
def test_model():
    flavor = Flavor(name="first-flavor")
    flavor.save()

    str_data = dumps({"flavor": flavor})
    data = loads(str_data)
    flavor_data = data["flavor"]

    actual = _construct_model(Flavor, flavor_data)

    assert actual.pk == flavor.id
    assert actual.name == flavor.name
    assert actual.parent is None


@pytest.mark.django_db
def test_model_foreign_key():
    parent = Flavor(name="parent-flavor")
    parent.save()
    flavor = Flavor(name="first-flavor", parent=parent)
    flavor.save()

    str_data = dumps({"flavor": flavor})
    data = loads(str_data)
    flavor_data = data["flavor"]

    actual = _construct_model(Flavor, flavor_data)

    assert actual.pk == flavor.id
    assert actual.name == flavor.name
    assert actual.parent.pk == parent.id
    assert actual.parent.name == parent.name


@pytest.mark.django_db
def test_queryset():
    test_component = FakeComponent(component_name="test", component_id="model_lifecycle_test_queryset")
    assert test_component.flavors.count() == 0

    flavor = Flavor(name="qs-first-flavor")
    flavor.save()

    flavors = Flavor.objects.filter(name="qs-first-flavor")
    str_data = dumps({"flavors": flavors})
    data = loads(str_data)
    flavors_data = data["flavors"]

    set_property_from_data(test_component, "flavors", flavors_data)

    assert test_component.flavors.count() == 1
    assert test_component.flavors[0].uuid == str(flavor.uuid)
    assert test_component.flavors[0].id == flavor.id


@pytest.mark.django_db
def test_queryset_values():
    test_component = FakeComponent(component_name="test", component_id="model_lifecycle_test_queryset_values")
    assert test_component.flavors.count() == 0

    flavor = Flavor(name="values-first-flavor")
    flavor.save()

    flavors = Flavor.objects.filter(name="values-first-flavor").values("uuid")
    str_data = dumps({"flavors": flavors})
    data = loads(str_data)
    flavors_data = data["flavors"]

    set_property_from_data(test_component, "flavors", flavors_data)

    assert test_component.flavors.count() == 1
    assert test_component.flavors[0].uuid == str(flavor.uuid)
    assert test_component.flavors[0].id is None
