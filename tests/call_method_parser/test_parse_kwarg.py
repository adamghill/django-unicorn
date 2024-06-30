import pytest

from django_unicorn.call_method_parser import InvalidKwargError, parse_kwarg


def test_kwargs_string():
    expected = {"test": "1"}
    actual = parse_kwarg("test='1'")

    assert actual == expected
    assert isinstance(actual["test"], str)
    assert actual["test"] == "1"


def test_kwargs_int():
    expected = {"test": 2}
    actual = parse_kwarg("test=2")

    assert actual == expected
    assert isinstance(actual["test"], int)
    assert actual["test"] == 2


def test_kwargs_invalid_startswith_doublequote():
    with pytest.raises(InvalidKwargError) as e:
        parse_kwarg('"test"=2')

    assert e.type == InvalidKwargError


def test_kwargs_invalid_startswith_singlequote():
    with pytest.raises(InvalidKwargError) as e:
        parse_kwarg("'test'=2")

    assert e.type == InvalidKwargError


def test_kwargs_invalid_no_equal_sign():
    with pytest.raises(InvalidKwargError) as e:
        parse_kwarg("test")

    assert e.type == InvalidKwargError


def test_kwargs_invalid_internal_doublequote():
    with pytest.raises(InvalidKwargError) as e:
        parse_kwarg('te"st=1')

    assert e.type == InvalidKwargError


def test_kwargs_invalid_internal_singlequote():
    with pytest.raises(InvalidKwargError) as e:
        parse_kwarg("te'st=1")

    assert e.type == InvalidKwargError


def test_kwargs_skip_unparseable_value():
    expected = {"test": "some_context_variable"}
    actual = parse_kwarg("test=some_context_variable")

    assert actual == expected
    assert isinstance(actual["test"], str)
    assert actual["test"] == "some_context_variable"


def test_kwargs_raise_unparseable_value():
    with pytest.raises(ValueError) as e:
        parse_kwarg("test=some_context_variable", raise_if_unparseable=True)

    assert e.type is ValueError
