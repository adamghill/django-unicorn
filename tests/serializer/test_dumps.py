import pytest
from django.db.models import SET_NULL, ForeignKey, Model
from django.db.models.fields import CharField

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
    expected = '{"simple_test_model":{"model":"tests.simpletestmodel","pk":1,"fields":{"name":"abc"}}}'

    actual = serializer.dumps({"simple_test_model": simple_test_model})

    assert expected == actual


def test_model_foreign_key():
    test_model_one = ComplicatedTestModel(id=1, name="abc")
    test_model_two = ComplicatedTestModel(id=2, name="def", parent=test_model_one)
    expected = '{"test_model_two":{"model":"tests.complicatedtestmodel","pk":2,"fields":{"name":"def","parent":1}}}'

    actual = serializer.dumps({"test_model_two": test_model_two})

    assert expected == actual


def test_model_foreign_key_recurive_parents():
    test_model_one = ComplicatedTestModel(id=1, name="abc")
    test_model_two = ComplicatedTestModel(id=2, name="def", parent=test_model_one)
    test_model_one.parent = test_model_two
    expected = '{"test_model_two":{"model":"tests.complicatedtestmodel","pk":2,"fields":{"name":"def","parent":1}}}'

    actual = serializer.dumps({"test_model_two": test_model_two})

    assert expected == actual


@pytest.mark.django_db
def test_dumps_queryset(db):
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()

    flavor_two = Flavor(name="name2", label="label2", parent=flavor_one)
    flavor_two.save()

    flavors = Flavor.objects.all()

    expected = '{"flavors":[{"model":"coffee.flavor","pk":1,"fields":{"name":"name1","label":"label1","parent":null}},{"model":"coffee.flavor","pk":2,"fields":{"name":"name2","label":"label2","parent":1}}]}'
    actual = serializer.dumps({"flavors": flavors})

    assert expected == actual


def test_get_model_dict():
    flavor_one = Flavor(name="name1", label="label1")
    actual = serializer._get_model_dict(flavor_one)

    expected = {
        "model": "coffee.flavor",
        "pk": None,
        "fields": {"name": "name1", "label": "label1", "parent": None},
    }

    assert expected == actual
