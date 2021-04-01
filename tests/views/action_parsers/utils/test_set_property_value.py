from datetime import datetime
from typing import List

import pytest

from django_unicorn.components import UnicornView
from django_unicorn.views.action_parsers.utils import set_property_value
from example.coffee.models import Flavor


class FakeComponent(UnicornView):
    string = "property_view"
    integer = 99
    datetime = datetime(2020, 1, 1)
    array: List[str] = []
    model = Flavor(name="initial-flavor")
    queryset = Flavor.objects.none()


def test_set_property_value_str():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert "property_view" == component.string

    set_property_value(
        component,
        "string",
        "property_view_updated",
        {"string": "property_view_updated"},
    )

    assert "property_view_updated" == component.string


def test_set_property_value_int():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert 99 == component.integer

    set_property_value(component, "integer", 100, {"integer": 100})

    assert 100 == component.integer


def test_set_property_value_datetime():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert datetime(2020, 1, 1) == component.datetime

    set_property_value(
        component, "datetime", datetime(2020, 1, 2), {"datetime": datetime(2020, 1, 2)}
    )

    assert datetime(2020, 1, 2) == component.datetime


def test_set_property_value_model():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert "initial-flavor" == component.model.name

    set_property_value(
        component,
        "model",
        Flavor(name="test-flavor"),
        {"model": {"name": "test-flavor"}},
    )

    assert "test-flavor" == component.model.name


@pytest.mark.django_db
def test_set_property_value_queryset():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert len(component.queryset) == 0

    flavor_one = Flavor(name="test-flavor-one")
    flavor_one.save()
    flavor_two = Flavor(name="test-flavor-two")
    flavor_two.save()
    queryset = Flavor.objects.all()[:2]

    set_property_value(
        component,
        "queryset",
        queryset,
        {"queryset": [{"name": "test-flavor-one"}, {"name": "test-flavor-two"}]},
    )

    assert len(queryset) == 2
