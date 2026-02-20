from dataclasses import dataclass

import pytest

from django_unicorn.components import UnicornView
from django_unicorn.views.action_parsers.utils import set_property_value
from example.coffee.models import Flavor


@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""

    name: str
    unit_price: float
    quantity_on_hand: int = 0


class PropertyView(UnicornView):
    inventory = InventoryItem("Hammer", 20)


class FakeComponent(UnicornView):
    flavors = []  # noqa: RUF012

    def __init__(self, **kwargs):
        self.flavors = list(Flavor.objects.all())

        super().__init__(**kwargs)


def test_set_property_value_dataclass():
    component = PropertyView(component_name="test", component_id="test_set_property_value_dataclass")
    assert InventoryItem("Hammer", 20) == component.inventory

    set_property_value(
        component,
        "inventory",
        InventoryItem("Hammer", 20, 1),
        {"inventory": InventoryItem("Hammer", 20, 1)},
    )

    assert InventoryItem("Hammer", 20, 1) == component.inventory


@pytest.mark.django_db
def test_set_property_value_array():
    flavor_one = Flavor(name="initial 1")
    flavor_one.save()
    flavor_two = Flavor(name="initial 2")
    flavor_two.save()
    component = FakeComponent(component_name="test", component_id="test_set_property_value_array")

    set_property_value(
        component,
        "flavors.0.name",
        "test 1",
        {"flavors": [{"name": "test"}, {"name": "something"}]},
    )

    assert component.flavors[0].name == "test 1"


@pytest.mark.django_db
def test_set_property_value_foreign_key():
    flavor = Flavor(name="initial 1")
    flavor.save()
    parent = Flavor(name="initial 2")
    parent.save()
    component = FakeComponent(component_name="test", component_id="test_set_property_value_foreign_key")

    set_property_value(
        component,
        "flavors.0.parent",
        parent.pk,
        {
            "flavors": [
                {"name": flavor.name, "parent": None},
            ]
        },
    )

    assert component.flavors[0].parent_id == parent.pk

    # This fails for Django 2.2, but not 3.0
    # assert component.flavors[0].parent.pk == parent.pk
