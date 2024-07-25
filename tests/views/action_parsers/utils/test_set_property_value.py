from datetime import datetime
from typing import List

import pytest

from django_unicorn.components import UnicornView
from django_unicorn.views.action_parsers.utils import set_property_value
from example.coffee.models import Flavor, Taste


class FakeComponent(UnicornView):
    string = "property_view"
    integer = 99
    datetime = datetime(2020, 1, 1)  # noqa: DTZ001
    array: List[str] = []  # noqa: RUF012
    model = Flavor(name="initial-flavor")
    queryset = Flavor.objects.none()
    taste = Taste(name="bitter")


def test_set_property_value_str():
    component = FakeComponent(component_name="test", component_id="test_set_property_value_str")
    assert "property_view" == component.string

    string = "property_view_updated"
    data = {"string": "property_view_updated"}

    set_property_value(
        component,
        "string",
        string,
        data,
    )

    assert component.string == string
    assert data["string"] == string


def test_set_property_value_int():
    component = FakeComponent(component_name="test", component_id="test_set_property_value_int")
    assert 99 == component.integer

    integer = 100
    data = {"integer": None}

    set_property_value(component, "integer", integer, data)

    assert component.integer == integer
    assert data["integer"] == integer


def test_set_property_value_datetime():
    component = FakeComponent(component_name="test", component_id="test_set_property_value_datetime")
    assert datetime(2020, 1, 1) == component.datetime  # noqa: DTZ001

    dt = datetime(2020, 1, 2)  # noqa: DTZ001
    data = {"datetime": None}

    set_property_value(component, "datetime", dt, data)

    assert component.datetime == dt
    assert data["datetime"] == dt


def test_set_property_value_model():
    component = FakeComponent(component_name="test", component_id="test_set_property_value_model")
    assert "initial-flavor" == component.model.name

    model = Flavor(name="test-flavor")
    data = {"model": {}}

    set_property_value(
        component,
        "model",
        model,
        data,
    )

    assert component.model.name == model.name
    assert data["model"] == model


@pytest.mark.django_db
def test_set_property_value_queryset():
    component = FakeComponent(component_name="test", component_id="test_set_property_value_queryset")
    assert len(component.queryset) == 0

    flavor_one = Flavor(name="test-flavor-one")
    flavor_one.save()
    flavor_two = Flavor(name="test-flavor-two")
    flavor_two.save()
    queryset = Flavor.objects.all()[:2]
    data = {"queryset": []}

    set_property_value(
        component,
        "queryset",
        queryset,
        data,
    )

    assert len(queryset) == 2
    assert data["queryset"] == queryset


@pytest.mark.django_db
def test_set_property_value_many_to_many_is_referenced():
    component = FakeComponent(component_name="test", component_id="test_set_property_value_many_to_many_is_referenced")
    component.model.save()
    assert component.model.taste_set.count() == 0

    taste = Taste(name="Bitter")
    taste.save()
    flavor = Flavor(name="test-flavor")
    flavor.save()
    flavor.taste_set.add(taste)

    data = {"model": {}}

    set_property_value(
        component,
        "model.taste_set",
        [taste.pk],
        data,
    )

    assert data["model"]["taste_set"] == [taste.pk]
    assert component.model.taste_set.count() == 1


@pytest.mark.django_db
def test_set_property_value_many_to_many_references_model():
    component = FakeComponent(
        component_name="test", component_id="test_set_property_value_many_to_many_references_model"
    )
    component.taste.save()
    assert component.taste.flavor.count() == 0

    taste = Taste(name="Bitter")
    taste.save()
    flavor = Flavor(name="test-flavor")
    flavor.save()
    flavor.taste_set.add(taste)

    data = {"taste": {}}

    set_property_value(
        component,
        "taste.flavor",
        [flavor.pk],
        data,
    )

    assert data["taste"]["flavor"] == [flavor.pk]
    assert component.taste.flavor.count() == 1
