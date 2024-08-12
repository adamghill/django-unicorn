import sys
from datetime import datetime, timezone
from typing import List

import pytest
from django.db.models import Model, QuerySet

from django_unicorn.components import UnicornView
from django_unicorn.typing import QuerySetType
from django_unicorn.views.utils import set_property_from_data
from example.coffee.models import Flavor


class FakeComponent(UnicornView):
    string = "property_view"
    integer = 99
    datetime_without_typehint = datetime(2020, 1, 1, tzinfo=timezone.utc)
    datetime_with_typehint: datetime = datetime(2020, 2, 1, tzinfo=timezone.utc)
    array: List[str] = []  # noqa: RUF012
    model = Flavor(name="test-initial")
    queryset = Flavor.objects.none()
    queryset_with_typehint: QuerySetType[Flavor] = []  # noqa: RUF012
    datetimes = [datetime(2020, 3, 1, tzinfo=timezone.utc)]  # noqa: RUF012
    datetimes_with_old_typehint: List[datetime] = [datetime(2020, 4, 1, tzinfo=timezone.utc)]  # noqa: RUF012
    datetimes_with_list_typehint: list = [datetime(2020, 6, 1, tzinfo=timezone.utc)]  # noqa: RUF012

    try:
        datetimes_with_new_typehint: list[datetime] = [datetime(2020, 5, 1, tzinfo=timezone.utc)]
    except TypeError:
        datetimes_with_new_typehint: None


class FakeQuerySetComponent(UnicornView):
    queryset_with_typehint: QuerySetType[Flavor] = None


class FakeDbComponent(UnicornView):
    queryset_with_data = Flavor.objects.none()

    def __init__(self, **kwargs):
        flavor = Flavor(pk=1, name="initial-test-data")
        flavor.save()
        self.queryset_with_data = Flavor.objects.filter()[:1]
        super().__init__(**kwargs)


class FakeAllQuerySetComponent(UnicornView):
    queryset_with_empty_list: QuerySetType[Flavor] = []  # noqa: RUF012
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
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_str")
    assert "property_view" == component.string

    set_property_from_data(component, "string", "property_view_updated")

    assert "property_view_updated" == component.string


def test_set_property_from_data_int():
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_int")
    assert 99 == component.integer

    set_property_from_data(component, "integer", 100)

    assert 100 == component.integer


def test_set_property_from_data_datetime():
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_datetime")
    assert datetime(2020, 1, 1, tzinfo=timezone.utc) == component.datetime_without_typehint

    set_property_from_data(
        component,
        "datetime_without_typehint",
        datetime(2020, 1, 2, tzinfo=timezone.utc),
    )

    assert datetime(2020, 1, 2, tzinfo=timezone.utc) == component.datetime_without_typehint


def test_set_property_from_data_datetime_with_typehint():
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_datetime_with_typehint")
    assert datetime(2020, 2, 1, tzinfo=timezone.utc) == component.datetime_with_typehint

    set_property_from_data(
        component,
        "datetime_with_typehint",
        str(datetime(2020, 2, 2, tzinfo=timezone.utc)),
    )

    assert datetime(2020, 2, 2, tzinfo=timezone.utc) == component.datetime_with_typehint


def test_set_property_from_data_list():
    """
    Prevent attempting to instantiate `List[]` type-hint doesn't throw TypeError
    """
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_list")
    assert component.array == []

    set_property_from_data(component, "array", ["string"])

    assert ["string"] == component.array


def test_set_property_from_data_list_datetimes():
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_list_datetimes")
    assert [datetime(2020, 3, 1, tzinfo=timezone.utc)] == component.datetimes

    set_property_from_data(component, "datetimes", [str(datetime(2020, 3, 2, tzinfo=timezone.utc))])

    assert [str(datetime(2020, 3, 2, tzinfo=timezone.utc))] == component.datetimes


def test_set_property_from_data_list_datetimes_with_old_typehint():
    component = FakeComponent(
        component_name="test", component_id="test_set_property_from_data_list_datetimes_with_old_typehint"
    )
    assert [datetime(2020, 4, 1, tzinfo=timezone.utc)] == component.datetimes_with_old_typehint

    set_property_from_data(
        component,
        "datetimes_with_old_typehint",
        [str(datetime(2020, 4, 2, tzinfo=timezone.utc))],
    )

    assert [datetime(2020, 4, 2, tzinfo=timezone.utc)] == component.datetimes_with_old_typehint


@pytest.mark.skipif(
    sys.version_info.major == 3 and sys.version_info.minor <= 8,  # noqa: YTT204
    reason="Skip new type hints for Python 3.8 or less",
)
def test_set_property_from_data_list_datetimes_with_new_typehint():
    component = FakeComponent(
        component_name="test", component_id="test_set_property_from_data_list_datetimes_with_new_typehint"
    )
    assert [datetime(2020, 5, 1, tzinfo=timezone.utc)] == component.datetimes_with_new_typehint

    set_property_from_data(
        component,
        "datetimes_with_new_typehint",
        [str(datetime(2020, 5, 2, tzinfo=timezone.utc))],
    )

    assert [datetime(2020, 5, 2, tzinfo=timezone.utc)] == component.datetimes_with_new_typehint


def test_set_property_from_data_list_datetimes_with_list_typehint():
    component = FakeComponent(
        component_name="test", component_id="test_set_property_from_data_list_datetimes_with_list_typehint"
    )
    assert [datetime(2020, 6, 1, tzinfo=timezone.utc)] == component.datetimes_with_list_typehint

    set_property_from_data(
        component,
        "datetimes_with_list_typehint",
        [str(datetime(2020, 6, 2, tzinfo=timezone.utc))],
    )

    assert [str(datetime(2020, 6, 2, tzinfo=timezone.utc))] == component.datetimes_with_list_typehint


def test_set_property_from_data_model():
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_model")
    assert component.model.name == "test-initial"

    set_property_from_data(component, "model", {"name": "test-test"})

    assert isinstance(component.model, Model)
    assert isinstance(component.model, Flavor)
    assert component.model.name == "test-test"


def test_set_property_from_data_empty_queryset():
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_empty_queryset")
    assert len(component.queryset) == 0

    set_property_from_data(component, "queryset", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset")


@pytest.mark.django_db
def test_set_property_from_data_queryset():
    component = FakeDbComponent(component_name="test", component_id="test_set_property_from_data_queryset")
    assert len(component.queryset_with_data) == 1

    set_property_from_data(component, "queryset_with_data", [{"pk": 1, "name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset_with_data")


def test_set_property_from_data_queryset_list_with_typehint():
    component = FakeComponent(
        component_name="test", component_id="test_set_property_from_data_queryset_list_with_typehint"
    )
    assert len(component.queryset_with_typehint) == 0

    set_property_from_data(component, "queryset_with_typehint", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset_with_typehint")


def test_set_property_from_data_queryset_none_with_typehint():
    component = FakeQuerySetComponent(
        component_name="test", component_id="test_set_property_from_data_queryset_none_with_typehint"
    )
    assert component.queryset_with_typehint is None

    set_property_from_data(component, "queryset_with_typehint", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset_with_typehint")


def test_set_property_from_data_queryset_parent():
    component = FakeQuerySetComponent(component_name="test", component_id="test_set_property_from_data_queryset_parent")
    assert component.queryset_with_typehint is None

    set_property_from_data(component, "queryset_with_typehint", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset_with_typehint")


def test_set_property_from_data_all_querysets():
    component = FakeAllQuerySetComponent(
        component_name="test", component_id="test_set_property_from_data_all_querysets"
    )

    set_property_from_data(component, "queryset_with_empty_list", [{"name": "test-qs"}])
    set_property_from_data(component, "queryset_with_none", [{"name": "test-qs"}])
    set_property_from_data(component, "queryset_with_empty_queryset", [{"name": "test-qs"}])
    set_property_from_data(component, "queryset_with_no_typehint", [{"name": "test-qs"}])

    component_queryset_field_asserts(component, "queryset_with_empty_list")
    component_queryset_field_asserts(component, "queryset_with_none")
    component_queryset_field_asserts(component, "queryset_with_empty_queryset")
    component_queryset_field_asserts(component, "queryset_with_no_typehint")


@pytest.mark.django_db
def test_set_property_from_data_many_to_many():
    component = FakeComponent(component_name="test", component_id="test_set_property_from_data_many_to_many")
    component.model.pk = 1

    # No `TypeError: Direct assignment to the reverse side of a many-to-many set is prohibited.` error gets raised
    set_property_from_data(component.model, "taste_set", [])
