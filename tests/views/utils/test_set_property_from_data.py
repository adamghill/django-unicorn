from datetime import datetime
from typing import List

from django.db.models import Model, QuerySet

import pytest

from django_unicorn.components import QuerySetType, UnicornView
from django_unicorn.views.utils import set_property_from_data
from example.coffee.models import Flavor


class FakeComponent(UnicornView):
    string = "property_view"
    integer = 99
    datetime = datetime(2020, 1, 1)
    array: List[str] = []
    model = Flavor(name="test-initial")
    queryset = Flavor.objects.none()
    queryset_with_typehint: QuerySetType[Flavor] = []


class FakeQuerySetComponent(UnicornView):
    queryset_with_typehint: QuerySetType[Flavor] = None


class FakeDbComponent(UnicornView):
    queryset_with_data = Flavor.objects.none()

    def __init__(self, *args, **kwargs):
        flavor = Flavor(pk=1, name="initial-test-data")
        flavor.save()
        self.queryset_with_data = Flavor.objects.filter()[:1]
        super().__init__(**kwargs)


class FakeAllQuerySetComponent(UnicornView):
    queryset_with_empty_list: QuerySetType[Flavor] = []
    queryset_with_none: QuerySetType[Flavor] = None
    queryset_with_empty_queryset: QuerySetType[Flavor] = Flavor.objects.none()
    queryset_with_no_typehint = Flavor.objects.none()


def component_queryset_field_asserts(component, field_name):
    field = getattr(component, field_name)
    assert isinstance(field, QuerySet)
    assert field.model == Flavor
    assert len(field) == 1
    assert field[0].name == "test-qs"


def test_set_property_from_data_str():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert "property_view" == component.string

    set_property_from_data(component, "string", "property_view_updated")

    assert "property_view_updated" == component.string


def test_set_property_from_data_int():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert 99 == component.integer

    set_property_from_data(component, "integer", 100)

    assert 100 == component.integer


def test_set_property_from_data_datetime():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert datetime(2020, 1, 1) == component.datetime

    set_property_from_data(component, "datetime", datetime(2020, 1, 2))

    assert datetime(2020, 1, 2) == component.datetime


def test_set_property_from_data_list():
    """
    Prevent attempting to instantiate `List[]` type-hint doesn't throw TypeError
    """
    component = FakeComponent(component_name="test", component_id="12345678")
    assert component.array == []

    set_property_from_data(component, "array", ["string"])

    assert ["string"] == component.array


def test_set_property_from_data_model():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert component.model.name == "test-initial"

    set_property_from_data(component, "model", {"name": "test-test"})

    assert isinstance(component.model, Model)
    assert isinstance(component.model, Flavor)
    assert component.model.name == "test-test"


def test_set_property_from_data_empty_queryset():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert len(component.queryset) == 0

    set_property_from_data(component, "queryset", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset")


@pytest.mark.django_db
def test_set_property_from_data_queryset():
    component = FakeDbComponent(component_name="test", component_id="12345678")
    assert len(component.queryset_with_data) == 1

    set_property_from_data(
        component, "queryset_with_data", [{"pk": 1, "name": "test-qs"}]
    )

    component_queryset_field_asserts(component, "queryset_with_data")


def test_set_property_from_data_queryset_list_with_typehint():
    component = FakeComponent(component_name="test", component_id="12345678")
    assert len(component.queryset_with_typehint) == 0

    set_property_from_data(component, "queryset_with_typehint", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset_with_typehint")


def test_set_property_from_data_queryset_none_with_typehint():
    component = FakeQuerySetComponent(component_name="test", component_id="12345678")
    assert component.queryset_with_typehint is None

    set_property_from_data(component, "queryset_with_typehint", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset_with_typehint")


def test_set_property_from_data_all_querysets():
    component = FakeAllQuerySetComponent(component_name="test", component_id="12345678")

    set_property_from_data(component, "queryset_with_empty_list", [{"name": "test-qs"}])
    set_property_from_data(component, "queryset_with_none", [{"name": "test-qs"}])
    set_property_from_data(
        component, "queryset_with_empty_queryset", [{"name": "test-qs"}]
    )
    set_property_from_data(
        component, "queryset_with_no_typehint", [{"name": "test-qs"}]
    )

    component_queryset_field_asserts(component, "queryset_with_empty_list")
    component_queryset_field_asserts(component, "queryset_with_none")
    component_queryset_field_asserts(component, "queryset_with_empty_queryset")
    component_queryset_field_asserts(component, "queryset_with_no_typehint")
