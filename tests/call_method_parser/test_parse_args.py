from datetime import datetime
from uuid import UUID

from django_unicorn.call_method_parser import eval_value


def test_args():
    expected = (1, 2)
    actual = eval_value("1, 2")

    assert actual == expected
    assert isinstance(actual[0], int)
    assert isinstance(actual[1], int)


def test_single_quote_str_arg():
    expected = "1"
    actual = eval_value("'1'")

    assert actual == expected
    assert isinstance(actual, str)


def test_str_with_space_arg():
    expected = "django unicorn"
    actual = eval_value("'django unicorn'")

    assert actual == expected
    assert isinstance(actual, str)


def test_str_with_extra_single_quote():
    expected = "django's unicorn"
    actual = eval_value("'django\\'s unicorn'")

    assert actual == expected
    assert isinstance(actual, str)


def test_str_with_extra_double_quote():
    expected = 'django "unicorn"'
    actual = eval_value("'django \"unicorn\"'")

    assert actual == expected
    assert isinstance(actual[0], str)


def test_str_with_comma():
    expected = "'a', b'"
    actual = eval_value("'a', b'")

    assert actual == expected
    assert isinstance(actual[0], str)


def test_str_with_stop_character():
    expected = "'a'} b'"
    actual = eval_value("'a'} b'")

    assert actual == expected
    assert isinstance(actual[0], str)


def test_double_quote_str_arg():
    expected = "string"
    actual = eval_value('"string"')

    assert actual == expected
    assert isinstance(actual, str)


def test_args_with_single_quote_dict():
    expected = (1, {"2": 3})
    actual = eval_value("1, {'2': 3}")

    assert actual == expected
    assert isinstance(actual[1], dict)


def test_args_with_double_quote_dict():
    expected = (1, {"2": 3})
    actual = eval_value('1, {"2": 3}')

    assert actual == expected
    assert isinstance(actual[1], dict)


def test_args_with_nested_dict():
    expected = (1, {"2": {"3": 4}})
    actual = eval_value("1, {'2': { '3': 4 }}")

    assert actual == expected
    assert isinstance(actual[1], dict)
    assert isinstance(actual[1].get("2"), dict)


def test_args_with_nested_list_3():
    expected = ([1, ["2", "3"], 4], 9)
    actual = eval_value("[1, ['2', '3'], 4], 9")

    assert actual == expected


def test_args_with_nested_tuple():
    expected = (9, (1, ("2", "3"), 4))
    actual = eval_value("9, (1, ('2', '3'), 4)")

    assert actual == expected


def test_args_with_nested_objects():
    expected = ([0, 1], {"2 2": {"3": 4}}, (5, 6, [7, 8]))
    actual = eval_value("[0,  1], {'2 2': { '3': 4 }}, (5, 6, [7, 8])")

    assert actual == expected


def test_list_args():
    expected = (1, [2, "3"])
    actual = eval_value("1, [2, '3']")

    assert actual == expected


def test_datetime():
    expected = datetime(2020, 9, 12, 1, 1, 1)  # noqa: DTZ001
    actual = eval_value("2020-09-12T01:01:01")

    assert actual == expected
    assert isinstance(actual, datetime)


def test_uuid():
    expected = UUID("90144cb9-fc47-476d-b124-d543b0cff091")
    actual = eval_value("90144cb9-fc47-476d-b124-d543b0cff091")

    assert actual == expected
    assert isinstance(actual, UUID)


def test_float():
    expected = [1, 5.4]
    actual = eval_value("[1, 5.4]")

    assert actual == expected
    assert isinstance(actual[1], float)


def test_set():
    expected = {1, 5}
    actual = eval_value("{1, 5}")

    assert actual == expected
    assert isinstance(actual, set)
