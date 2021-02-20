from dataclasses import dataclass

from django_unicorn.components import UnicornView
from django_unicorn.views import _set_property_value


@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""
    name: str
    unit_price: float
    quantity_on_hand: int = 0


class NestedPropertyView(UnicornView):
    inventory = InventoryItem("Hammer", 20)


def test_set_property_value_dataclass():
    component = NestedPropertyView(component_name="test", component_id="12345678")
    assert InventoryItem("Hammer", 20) == component.inventory

    _set_property_value(
        component, "inventory",
        InventoryItem("Hammer", 20, 1),
        {"inventory": InventoryItem("Hammer", 20, 1)}
    )

    assert InventoryItem("Hammer", 20, 1) == component.inventory
