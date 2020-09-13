# from datetime import datetime
# from decimal import Decimal

# import pytest

from django_unicorn.call_method_parser import parse_call_method_name

# from django_unicorn.errors import UnicornViewError


def test_single_int_arg():
    expected = ("set_name", [1])
    actual = parse_call_method_name("set_name(1)")

    assert actual == expected


def test_single_dict_arg():
    expected = ("set_name", [{"1": 2, "3": 4}])
    actual = parse_call_method_name('set_name({"1": 2, "3": 4})')

    assert actual == expected


def test_multiple_args():
    expected = ("set_name", [0, {"1": 2}])
    actual = parse_call_method_name('set_name(0, {"1": 2})')

    assert actual == expected


def test_one_arg():
    expected = ("set_name", ["1",])
    actual = parse_call_method_name('set_name("1")')

    assert actual == expected


def test_multiple_args():
    expected = ("set_name", [1, 2])
    actual = parse_call_method_name("set_name(1, 2)")

    assert actual == expected
