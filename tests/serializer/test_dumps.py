import json
from decimal import Decimal

from django.db import models
from django.utils.timezone import now

import pytest

from django_unicorn import serializer
from django_unicorn.utils import dicts_equal
from example.coffee.models import Flavor, Taste


class SimpleTestModel(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        app_label = "tests"


class ComplicatedTestModel(models.Model):
    name = models.CharField(max_length=10)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = "tests"


def test_int():
    expected = '{"name":123}'
    actual = serializer.dumps({"name": 123})

    assert expected == actual


def test_decimal():
    expected = '{"name":"123.1"}'
    actual = serializer.dumps({"name": Decimal("123.1")})

    assert expected == actual


def test_string():
    expected = '{"name":"abc"}'
    actual = serializer.dumps({"name": "abc"})

    assert expected == actual


def test_list():
    expected = '{"name":["abc","def"]}'
    actual = serializer.dumps({"name": ["abc", "def",]})

    assert expected == actual


def test_simple_model():
    simple_test_model = SimpleTestModel(id=1, name="abc")
    expected = '{"simple_test_model":{"name":"abc","pk":1}}'

    actual = serializer.dumps({"simple_test_model": simple_test_model})

    assert expected == actual


def test_model_with_datetime(db):
    datetime = now()
    flavor = Flavor(name="name1", datetime=datetime)

    expected = {
        "flavor": {
            "name": "name1",
            "label": "",
            "parent": None,
            "float_value": None,
            "decimal_value": None,
            "uuid": str(flavor.uuid),
            "date": None,
            "datetime": datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "time": None,
            "duration": None,
            "pk": None,
            "taste_set": [],
            "origins": [],
        }
    }

    actual = serializer.dumps({"flavor": flavor})
    assert dicts_equal(expected, json.loads(actual))


def test_model_with_datetime_as_string(db):
    datetime = now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    flavor = Flavor(name="name1", datetime=datetime)

    expected = {
        "flavor": {
            "name": "name1",
            "label": "",
            "parent": None,
            "float_value": None,
            "decimal_value": None,
            "uuid": str(flavor.uuid),
            "date": None,
            "datetime": datetime,
            "time": None,
            "duration": None,
            "pk": None,
            "taste_set": [],
            "origins": [],
        }
    }

    actual = serializer.dumps({"flavor": flavor})
    assert dicts_equal(expected, json.loads(actual))


def test_model_with_time_as_string(db):
    time = now().strftime("%H:%M:%S.%f")[:-3]
    flavor = Flavor(name="name1", time=time)

    expected = {
        "flavor": {
            "name": "name1",
            "label": "",
            "parent": None,
            "float_value": None,
            "decimal_value": None,
            "uuid": str(flavor.uuid),
            "date": None,
            "datetime": None,
            "time": time,
            "duration": None,
            "pk": None,
            "taste_set": [],
            "origins": [],
        }
    }

    actual = serializer.dumps({"flavor": flavor})
    assert dicts_equal(expected, json.loads(actual))


def test_model_with_duration_as_string(db):
    duration = "-1 day, 19:00:00"
    flavor = Flavor(name="name1", duration=duration)

    expected = {
        "flavor": {
            "name": "name1",
            "label": "",
            "parent": None,
            "float_value": None,
            "decimal_value": None,
            "uuid": str(flavor.uuid),
            "date": None,
            "datetime": None,
            "time": None,
            "duration": "-1 19:00:00",
            "pk": None,
            "taste_set": [],
            "origins": [],
        }
    }

    actual = serializer.dumps({"flavor": flavor})
    assert dicts_equal(expected, json.loads(actual))


def test_model_foreign_key():
    test_model_one = ComplicatedTestModel(id=1, name="abc")
    test_model_two = ComplicatedTestModel(id=2, name="def", parent=test_model_one)
    expected = '{"test_model_two":{"name":"def","parent":1,"pk":2}}'

    actual = serializer.dumps({"test_model_two": test_model_two})

    assert expected == actual


def test_model_foreign_key_recursive_parent():
    test_model_one = ComplicatedTestModel(id=1, name="abc")
    test_model_two = ComplicatedTestModel(id=2, name="def", parent=test_model_one)
    test_model_one.parent = test_model_two
    expected = '{"test_model_two":{"name":"def","parent":1,"pk":2}}'

    actual = serializer.dumps({"test_model_two": test_model_two})

    assert expected == actual


@pytest.mark.django_db
def test_dumps_queryset(db):
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()

    flavor_two = Flavor(name="name2", label="label2", parent=flavor_one)
    flavor_two.save()

    flavors = Flavor.objects.all()

    expected_data = {
        "flavors": [
            {
                "name": "name1",
                "label": "label1",
                "parent": None,
                "float_value": None,
                "decimal_value": None,
                "uuid": str(flavor_one.uuid),
                "date": None,
                "datetime": None,
                "time": None,
                "duration": None,
                "pk": 1,
                "taste_set": [],
                "origins": [],
            },
            {
                "name": "name2",
                "label": "label2",
                "parent": 1,
                "float_value": None,
                "decimal_value": None,
                "uuid": str(flavor_two.uuid),
                "date": None,
                "datetime": None,
                "time": None,
                "duration": None,
                "pk": 2,
                "taste_set": [],
                "origins": [],
            },
        ]
    }

    actual = serializer.dumps({"flavors": flavors})
    assert expected_data == json.loads(actual)


def test_get_model_dict():
    flavor_one = Flavor(name="name1", label="label1")
    actual = serializer._get_model_dict(flavor_one)

    expected = {
        "pk": None,
        "name": "name1",
        "label": "label1",
        "parent": None,
        "decimal_value": None,
        "float_value": None,
        "uuid": str(flavor_one.uuid),
        "date": None,
        "datetime": None,
        "time": None,
        "duration": None,
        "taste_set": [],
        "origins": [],
    }

    assert expected == actual


@pytest.mark.django_db
def test_get_model_dict_many_to_many_is_referenced():
    taste = Taste(name="Bitter")
    taste.save()
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()
    flavor_one.taste_set.add(taste)
    actual = serializer._get_model_dict(flavor_one)

    expected = {
        "pk": 1,
        "name": "name1",
        "label": "label1",
        "parent": None,
        "decimal_value": None,
        "float_value": None,
        "uuid": str(flavor_one.uuid),
        "date": None,
        "datetime": None,
        "time": None,
        "duration": None,
        "taste_set": [taste.pk],
        "origins": [],
    }

    assert expected == actual


@pytest.mark.django_db
def test_get_model_dict_many_to_many_references_model():
    taste = Taste(name="Bitter")
    taste.save()
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()
    flavor_one.taste_set.add(taste)
    actual = serializer._get_model_dict(taste)

    expected = {"name": taste.name, "flavor": [flavor_one.pk], "pk": taste.pk}

    assert expected == actual


def test_float():
    expected = '{"name":"0.0"}'
    actual = serializer.dumps({"name": 0.0})

    assert expected == actual


def test_dict_float():
    expected = '{"name":{"another":"0.0"}}'
    actual = serializer.dumps({"name": {"another": 0.0}})

    assert expected == actual


def test_list_float():
    expected = '{"name":[1,2,"0.0"]}'
    actual = serializer.dumps({"name": [1, 2, 0.0]})

    assert expected == actual


def test_nested_list_float():
    expected = '{"name":{"blob":[1,2,"0.0"]}}'
    actual = serializer.dumps({"name": {"blob": [1, 2, 0.0]}})

    assert expected == actual


def test_nested_list_float_complicated():
    expected = '{"name":{"blob":[1,2,"0.0"]},"more":["1.9",2,5],"another":[{"great":"1.0","ok":["1.6","0.0",4]}]}'
    actual = serializer.dumps(
        {
            "name": {"blob": [1, 2, 0.0]},
            "more": [1.9, 2, 5],
            "another": [{"great": 1.0, "ok": [1.6, 0.0, 4]}],
        }
    )

    assert expected == actual


def test_nested_list_float_less_complicated():
    expected = '{"another":[{"great":"1.0","ok":["1.6","0.0",4]}]}'
    actual = serializer.dumps({"another": [{"great": 1.0, "ok": [1.6, 0.0, 4]}],})

    assert expected == actual


def test_pydantic():
    from pydantic import BaseModel

    class Book(BaseModel):
        title = "The Grapes of Wrath"
        author = "John Steinbeck"

    expected = '{"title":"The Grapes of Wrath","author":"John Steinbeck"}'
    actual = serializer.dumps(Book())

    assert expected == actual
