import json
from decimal import Decimal

from django.db import models
from django.utils.timezone import now

import pytest

from django_unicorn import serializer
from django_unicorn.serializer import InvalidFieldAttributeError, InvalidFieldNameError
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
    actual = serializer.dumps(
        {
            "name": [
                "abc",
                "def",
            ]
        }
    )

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
def test_model_many_to_many(django_assert_num_queries):
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()

    taste1 = Taste(name="Bitter1")
    taste1.save()
    taste2 = Taste(name="Bitter2")
    taste2.save()
    taste3 = Taste(name="Bitter3")
    taste3.save()

    flavor_one.taste_set.add(taste1)
    flavor_one.taste_set.add(taste2)
    flavor_one.taste_set.add(taste3)

    with django_assert_num_queries(2):
        actual = serializer.dumps(flavor_one)

    expected = {
        "name": "name1",
        "label": "label1",
        "parent": None,
        "float_value": None,
        "decimal_value": None,
        "uuid": str(flavor_one.uuid),
        "datetime": None,
        "date": None,
        "time": None,
        "duration": None,
        "pk": 1,
        "taste_set": [taste1.pk, taste2.pk, taste3.pk],
        "origins": [],
    }

    assert expected == json.loads(actual)


@pytest.mark.django_db
def test_model_many_to_many_with_excludes(django_assert_num_queries):
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()

    taste1 = Taste(name="Bitter1")
    taste1.save()
    taste2 = Taste(name="Bitter2")
    taste2.save()
    taste3 = Taste(name="Bitter3")
    taste3.save()

    flavor_one.taste_set.add(taste1)
    flavor_one.taste_set.add(taste2)
    flavor_one.taste_set.add(taste3)

    # This shouldn't make any database calls because the many-to-manys are excluded and
    # all of the other data is already set
    with django_assert_num_queries(0):
        actual = serializer.dumps(
            {"flavor": flavor_one},
            exclude_field_attributes=(
                "flavor.taste_set",
                "flavor.origins",
            ),
        )

    expected = {
        "flavor": {
            "name": "name1",
            "label": "label1",
            "parent": None,
            "float_value": None,
            "decimal_value": None,
            "uuid": str(flavor_one.uuid),
            "datetime": None,
            "date": None,
            "time": None,
            "duration": None,
            "pk": 1,
        }
    }

    assert expected == json.loads(actual)


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
def test_get_model_dict_many_to_many_is_referenced(django_assert_num_queries):
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()

    taste1 = Taste(name="Bitter")
    taste1.save()
    taste2 = Taste(name="Bitter2")
    taste2.save()
    taste3 = Taste(name="Bitter3")
    taste3.save()

    flavor_one.taste_set.add(taste1)
    flavor_one.taste_set.add(taste2)
    flavor_one.taste_set.add(taste3)

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
        "taste_set": [taste1.pk, taste2.pk, taste3.pk],
        "origins": [],
    }

    flavor_one = Flavor.objects.filter(id=flavor_one.id).first()

    with django_assert_num_queries(2):
        actual = serializer._get_model_dict(flavor_one)

    assert expected == actual


@pytest.mark.django_db
def test_get_model_dict_many_to_many_is_referenced_prefetched(
    django_assert_num_queries,
):
    flavor_one = Flavor(name="name1", label="label1")
    flavor_one.save()

    taste1 = Taste(name="Bitter")
    taste1.save()
    taste2 = Taste(name="Bitter2")
    taste2.save()
    taste3 = Taste(name="Bitter3")
    taste3.save()

    flavor_one.taste_set.add(taste1)
    flavor_one.taste_set.add(taste2)
    flavor_one.taste_set.add(taste3)

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
        "taste_set": [taste1.pk, taste2.pk, taste3.pk],
        "origins": [],
    }

    flavor_one = (
        Flavor.objects.prefetch_related("taste_set").filter(id=flavor_one.id).first()
    )

    # prefetch_related should reduce the database calls
    with django_assert_num_queries(1):
        actual = serializer._get_model_dict(flavor_one)

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
    actual = serializer.dumps(
        {
            "another": [{"great": 1.0, "ok": [1.6, 0.0, 4]}],
        }
    )

    assert expected == actual


def test_pydantic():
    from pydantic import BaseModel

    class Book(BaseModel):
        title = "The Grapes of Wrath"
        author = "John Steinbeck"

    expected = '{"title":"The Grapes of Wrath","author":"John Steinbeck"}'
    actual = serializer.dumps(Book())

    assert expected == actual


def test_exclude_field_attributes():
    expected = '{"book":{"title":"The Grapes of Wrath"}}'

    actual = serializer.dumps(
        {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
        exclude_field_attributes=("book.author",),
    )

    assert expected == actual


def test_exclude_field_attributes_no_fix_floats():
    expected = '{"book":{"title":"The Grapes of Wrath"}}'

    actual = serializer.dumps(
        {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
        fix_floats=False,
        exclude_field_attributes=("book.author",),
    )

    assert expected == actual


def test_exclude_field_attributes_nested():
    expected = '{"classic":{"book":{"title":"The Grapes of Wrath"}}}'

    actual = serializer.dumps(
        {
            "classic": {
                "book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}
            }
        },
        exclude_field_attributes=("classic.book.author",),
    )

    assert expected == actual


def test_exclude_field_attributes_invalid_field_attribute():
    expected = '{"book":{"title":"The Grapes of Wrath","author":"John Steinbeck"}}'

    actual = serializer.dumps(
        {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
        exclude_field_attributes=("blob",),
    )

    assert expected == actual


def test_exclude_field_attributes_empty_string():
    expected = '{"book":{"title":"The Grapes of Wrath","author":"John Steinbeck"}}'

    actual = serializer.dumps(
        {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
        exclude_field_attributes=("",),
    )

    assert expected == actual


def test_exclude_field_attributes_none():
    expected = '{"book":{"title":"The Grapes of Wrath","author":"John Steinbeck"}}'

    actual = serializer.dumps(
        {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
        exclude_field_attributes=None,
    )

    assert expected == actual


def test_exclude_field_attributes_invalid_name():
    with pytest.raises(InvalidFieldNameError) as e:
        serializer.dumps(
            {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
            exclude_field_attributes=("blob.monster",),
        )

    assert (
        e.exconly()
        == "django_unicorn.serializer.InvalidFieldNameError: Cannot resolve 'blob'. Choices are: book"
    )


def test_exclude_field_attributes_invalid_attribute():
    with pytest.raises(InvalidFieldAttributeError) as e:
        serializer.dumps(
            {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
            exclude_field_attributes=("book.blob",),
        )

    assert (
        e.exconly()
        == "django_unicorn.serializer.InvalidFieldAttributeError: Cannot resolve 'blob'. Choices on 'book' are: title, author"
    )


def test_exclude_field_attributes_invalid_type():
    with pytest.raises(AssertionError) as e:
        serializer.dumps(
            {"book": {"title": "The Grapes of Wrath", "author": "John Steinbeck"}},
            exclude_field_attributes=("book.blob"),
        )
