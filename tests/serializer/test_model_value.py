import pytest
from django.db import models

from django_unicorn.components import ModelValueMixin
from django_unicorn.serializer import model_value
from example.coffee.models import Flavor


def test_model_value_all_fields():
    flavor = Flavor(name="flavor-1")

    expected = {
        "date": None,
        "datetime": None,
        "decimal_value": None,
        "duration": None,
        "float_value": None,
        "name": flavor.name,
        "label": "",
        "parent": None,
        "pk": None,
        "time": None,
        "uuid": str(flavor.uuid),
        "taste_set": [],
        "origins": [],
    }

    actual = model_value(flavor)

    assert expected == actual


def test_model_value_one_field():
    expected = {"name": "flavor-1"}

    flavor = Flavor(name="flavor-1")
    actual = model_value(flavor, "name")

    assert expected == actual


@pytest.mark.django_db
def test_model_value_multiple_field():
    expected = {
        "pk": 77,
        "name": "flavor-1",
    }

    flavor = Flavor(name="flavor-1", id=77)
    actual = model_value(flavor, "pk", "name")

    assert expected == actual


class FakeModel(ModelValueMixin, models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "tests"


def test_model_value_mixin():
    test_model = FakeModel(name="test-model")
    expected = {"name": test_model.name}

    actual = test_model.value("name")
    assert expected == actual

    actual = model_value(test_model, "name")
    assert expected == actual
