from typing import Optional, get_type_hints

from django_unicorn.typer import cast_attribute_value, cast_value, get_type_hints
from example.coffee.models import Flavor


def test_get_type_hints():
    def test_func(input_str: str):
        return input_str

    expected = {"input_str": str}
    actual = get_type_hints(test_func)
    assert actual == expected


def test_get_type_hints_missing_type_hints():
    def test_func(input_str):
        return input_str

    expected = {}
    actual = get_type_hints(test_func)
    assert actual == expected


class TestClass:
    integer: int
    boolean: bool


def test_cast_attribute_value_int():
    expected = 1
    actual = cast_attribute_value(TestClass(), "integer", "1")

    assert expected == actual


def test_cast_attribute_value_bool_true():
    expected = True
    actual = cast_attribute_value(TestClass(), "boolean", "True")

    assert expected == actual


def test_cast_attribute_value_bool_false():
    expected = False
    actual = cast_attribute_value(TestClass(), "boolean", "False")

    assert expected == actual


def test_cast_attribute_value_bool_invalid():
    expected = False
    actual = cast_attribute_value(TestClass(), "boolean", "asdf")

    assert expected == actual

class ExampleClass:
    a_model: Flavor
    optional_model: Optional[Flavor]

def test_cast_value_model_none():
    example_class = ExampleClass()
    type_hints = get_type_hints(example_class)
    type_hint = type_hints["a_model"]

    actual = cast_value(type_hint, None)

    assert actual is None


def test_cast_value_optional():
    type_hints = get_type_hints(ExampleClass())
    type_hint = type_hints["optional_model"]

    actual = cast_value(type_hint, None)

    assert actual is None


def test_cast_value_model_int():
    example_class = ExampleClass()
    example_class.a_model = Flavor()

    type_hints = get_type_hints(example_class)
    type_hint = type_hints["optional_model"]

    actual = cast_value(type_hint, 1)

    assert actual == 1
