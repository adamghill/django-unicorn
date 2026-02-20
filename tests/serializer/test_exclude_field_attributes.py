import pytest

from django_unicorn.serializer import (
    InvalidFieldAttributeError,
    InvalidFieldNameError,
    _exclude_field_attributes,
)


def test_exclude_field_attributes():
    expected = {"1": {"2": {}}}
    dict_data = {"1": {"2": {"3": "4"}}}
    _exclude_field_attributes(dict_data, ("1.2.3",))

    assert dict_data == expected


def test_exclude_field_attributes_none_value():
    expected = {"1": None}
    dict_data = {"1": None}
    _exclude_field_attributes(dict_data, ("1.2",))

    assert dict_data == expected


def test_exclude_field_attributes_empty_value():
    dict_data = {"1": {}}

    with pytest.raises(InvalidFieldAttributeError):
        _exclude_field_attributes(dict_data, ("1.2",))


def test_exclude_field_attributes_invalid_field_name():
    dict_data = {"test": None}

    with pytest.raises(InvalidFieldNameError):
        _exclude_field_attributes(dict_data, ("1.2",))


def test_exclude_field_attributes_invalid_field_attribute():
    dict_data = {"1": {"test": "more"}}

    with pytest.raises(InvalidFieldAttributeError):
        _exclude_field_attributes(dict_data, ("1.2",))
