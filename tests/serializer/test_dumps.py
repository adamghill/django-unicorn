from django.db.models import SET_NULL, ForeignKey, Model
from django.db.models.fields import CharField

import pytest

from django_unicorn import serializer
from example.coffee.models import Flavor


class SimpleTestModel(Model):
    name = CharField(max_length=10)

    class Meta:
        app_label = "tests"


class ComplicatedTestModel(Model):
    name = CharField(max_length=10)
    parent = ForeignKey("self", blank=True, null=True, on_delete=SET_NULL)

    class Meta:
        app_label = "tests"


def test_int():
    expected = '{"name":123}'
    actual = serializer.dumps({"name": 123})

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


def test_model_foreign_key():
    test_model_one = ComplicatedTestModel(id=1, name="abc")
    test_model_two = ComplicatedTestModel(id=2, name="def", parent=test_model_one)
    expected = '{"test_model_two":{"name":"def","parent":1,"pk":2}}'

    actual = serializer.dumps({"test_model_two": test_model_two})

    assert expected == actual


def test_model_foreign_key_recurive_parents():
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

    expected = '{"flavors":[{"name":"name1","label":"label1","parent":null,"float_value":null,"decimal_value":null,"pk":1},{"name":"name2","label":"label2","parent":1,"float_value":null,"decimal_value":null,"pk":2}]}'
    actual = serializer.dumps({"flavors": flavors})

    assert expected == actual


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
    }

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
