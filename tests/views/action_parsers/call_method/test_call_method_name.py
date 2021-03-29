import pytest

from django_unicorn.components import UnicornView
from django_unicorn.views.action_parsers.call_method import _call_method_name
from example.coffee.models import Flavor


class FakeComponent(UnicornView):
    def save(self):
        return 1

    def save_with_arg(self, id):
        return 1 + id

    def save_with_kwarg(self, id=0):
        return 1 + id

    def save_with_model(self, model: Flavor):
        assert issubclass(type(model), Flavor), "model arg should be a `Flavor` model"
        return model.pk


def test_call_method_name_missing():
    component = FakeComponent(component_name="test", component_id="asdf")
    actual = _call_method_name(component, "save_missing", args=[], kwargs={})

    assert actual is None


def test_call_method_name_no_params():
    expected = 1

    component = FakeComponent(component_name="test", component_id="asdf")
    actual = _call_method_name(component, "save", args=[], kwargs={})

    assert actual == expected


def test_call_method_name_with_arg():
    expected = 2

    component = FakeComponent(component_name="test", component_id="asdf")
    actual = _call_method_name(component, "save_with_arg", args=[1], kwargs={})

    assert actual == expected


def test_call_method_name_with_kwarg():
    expected = 3

    component = FakeComponent(component_name="test", component_id="asdf")
    actual = _call_method_name(component, "save_with_kwarg", args=[], kwargs={"id": 2})

    assert actual == expected


@pytest.mark.django_db
def test_call_method_name_arg_with_model_type_annotation():
    flavor = Flavor()
    flavor.save()

    component = FakeComponent(component_name="test", component_id="asdf")
    actual = _call_method_name(
        component, "save_with_model", args=[flavor.pk], kwargs={}
    )

    assert actual == flavor.pk


@pytest.mark.django_db
def test_call_method_name_kwarg_with_model_type_annotation():
    flavor = Flavor()
    flavor.save()

    component = FakeComponent(component_name="test", component_id="asdf")
    actual = _call_method_name(
        component, "save_with_model", args=[], kwargs={"pk": flavor.pk}
    )

    assert actual == flavor.pk
