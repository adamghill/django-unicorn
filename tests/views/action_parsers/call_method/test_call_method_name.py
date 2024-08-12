from datetime import date, datetime, time, timedelta
from types import MappingProxyType
from typing import Optional, Union
from uuid import UUID, uuid4

import pytest

from django_unicorn.components import UnicornView
from django_unicorn.views.action_parsers.call_method import _call_method_name
from example.coffee.models import Flavor


class CustomClass:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class InvalidCustomClass:
    pass


class FakeComponent(UnicornView):
    def save(self):
        return 1

    def save_with_arg(self, id):  # noqa: A002
        return 1 + id

    def save_with_kwarg(self, id=0):  # noqa: A002
        return 1 + id

    def save_with_model(self, model: Flavor):
        assert issubclass(type(model), Flavor), "model arg should be a `Flavor` model"
        return model.pk

    def save_with_union(self, id: Union[int, str]):  # noqa: A002
        assert isinstance(id, (int, str))
        return id

    def get_datetime_without_type_hint(self, _datetime):
        return _datetime

    def get_datetime(self, _datetime: datetime):
        return _datetime

    def get_date(self, _date: date):
        return _date

    def get_datetime_and_date(self, _datetime: datetime, _date: date):
        return (_datetime, _date)

    def get_duration(self, _duration: timedelta):
        return _duration

    def get_time(self, _time: time):
        return _time

    def get_duration_and_time(self, _duration: Optional[timedelta] = None, _time: Optional[time] = None):
        return (_duration, _time)

    def get_uuid(self, _uuid: UUID):
        return _uuid

    def get_custom_class(self, _cls: CustomClass):
        return _cls

    def get_invalid_custom_class(self, _cls: InvalidCustomClass):
        return _cls


def test_call_method_name_missing():
    component = FakeComponent(component_name="test", component_id="test_call_method_name_missing")
    actual = _call_method_name(component, "save_missing", args=(), kwargs={})

    assert actual is None


def test_call_method_name_no_params():
    expected = 1

    component = FakeComponent(component_name="test", component_id="test_call_method_name_no_params")
    actual = _call_method_name(component, "save", args=(), kwargs={})

    assert actual == expected


def test_call_method_name_with_arg():
    expected = 2

    component = FakeComponent(component_name="test", component_id="test_call_method_name_with_arg")
    actual = _call_method_name(component, "save_with_arg", args=(1,), kwargs={})

    assert actual == expected


def test_call_method_name_with_kwarg():
    expected = 3

    component = FakeComponent(component_name="test", component_id="test_call_method_name_with_kwarg")
    actual = _call_method_name(component, "save_with_kwarg", args=(), kwargs=MappingProxyType({"id": 2}))

    assert actual == expected


@pytest.mark.django_db
def test_call_method_name_arg_with_model_type_annotation():
    flavor = Flavor()
    flavor.save()

    component = FakeComponent(
        component_name="test", component_id="test_call_method_name_arg_with_model_type_annotation"
    )
    actual = _call_method_name(component, "save_with_model", args=(flavor.pk,), kwargs={})

    assert actual == flavor.pk


@pytest.mark.django_db
def test_call_method_name_arg_with_model_type_annotation_multiple():
    flavor_one = Flavor()
    flavor_one.save()

    flavor_two = Flavor()
    flavor_two.save()

    assert flavor_one.pk != flavor_two.pk

    component = FakeComponent(
        component_name="test", component_id="test_call_method_name_arg_with_model_type_annotation_multiple"
    )
    actual = _call_method_name(component, "save_with_model", args=(flavor_one.pk,), kwargs={})
    assert actual == flavor_one.pk

    # second call
    actual = _call_method_name(component, "save_with_model", args=(flavor_two.pk,), kwargs={})
    assert actual == flavor_two.pk

    # third call
    actual = _call_method_name(component, "save_with_model", args=(flavor_one.pk,), kwargs={})
    assert actual == flavor_one.pk

    # fourth call
    actual = _call_method_name(component, "save_with_model", args=(flavor_one.pk,), kwargs={})
    assert actual == flavor_one.pk


def _get_actual(method_name: str, args=None, kwargs=None):
    component = FakeComponent(component_name="test", component_id="test-call-method-name-tests")

    if args is None:
        args = ()

    if kwargs is None:
        kwargs = {}

    return _call_method_name(
        component,
        method_name,
        args=args,
        kwargs=kwargs,
    )


@pytest.mark.django_db
def test_call_method_name_kwarg_with_model_type_annotation():
    flavor = Flavor()
    flavor.save()

    actual = _get_actual("save_with_model", kwargs=MappingProxyType({"pk": flavor.pk}))

    assert actual == flavor.pk


def test_call_method_name_with_kwarg_with_union_and_int():
    actual = _get_actual("save_with_union", kwargs=MappingProxyType({"id": 2}))

    assert isinstance(actual, int)


def test_call_method_name_with_kwarg_with_union_and_str():
    actual = _get_actual("save_with_union", kwargs=MappingProxyType({"id": "2"}))

    assert isinstance(actual, int)


def test_call_method_name_without_type_hint():
    actual = _get_actual("get_datetime_without_type_hint", args=["2020-09-12T01:01:01"])

    assert isinstance(actual, str)


def test_call_method_name_with_datetime_type_hint():
    actual = _get_actual("get_datetime", args=["2020-09-12T01:01:01"])

    assert isinstance(actual, datetime)


def test_call_method_name_with_date_type_hint():
    actual = _get_actual("get_date", args=["2020-09-12"])

    assert isinstance(actual, date)


def test_call_method_name_with_time_type_hint():
    actual = _get_actual("get_time", args=["01:01:01"])

    assert isinstance(actual, time)


def test_call_method_name_with_datetime_and_date_type_hint():
    actual = _get_actual("get_datetime_and_date", args=["2020-09-12T01:01:01", "2020-09-12"])

    assert isinstance(actual[0], datetime)
    assert isinstance(actual[1], date)


def test_call_method_name_with_duration_type_hint():
    actual = _get_actual("get_duration", args=["3"])

    assert isinstance(actual, timedelta)


def test_call_method_name_with_duration_and_time_type_hint():
    actual = _get_actual("get_duration_and_time", kwargs={"_duration": "3", "_time": "1:01:01"})

    assert isinstance(actual[0], timedelta)
    assert isinstance(actual[1], time)


def test_call_method_name_with_datetime_as_epoch_type_hint():
    actual = _get_actual("get_datetime", kwargs={"_datetime": 1691499534})

    assert isinstance(actual, datetime)


def test_call_method_name_with_date_as_epoch_type_hint():
    actual = _get_actual("get_date", kwargs={"_date": 1691499534})

    assert isinstance(actual, date)
    assert actual == date(2023, 8, 8)


def test_call_method_name_with_uuid_type_hint():
    actual = _get_actual("get_uuid", kwargs={"_uuid": str(uuid4())})

    assert isinstance(actual, UUID)


def test_call_method_name_with_custom_class_type_hint():
    actual = _get_actual("get_custom_class", kwargs={"_cls": "test"})

    assert isinstance(actual, CustomClass)
    assert actual.args[0] == "test"


def test_call_method_name_with_invalid_custom_class_type_hint():
    with pytest.raises(TypeError):
        _get_actual("get_invalid_custom_class", kwargs={"_cls": "test"})
