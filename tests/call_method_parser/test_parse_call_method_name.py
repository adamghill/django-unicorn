from django_unicorn.call_method_parser import parse_call_method_name


def setup_function():
    """Clears lru_cache before every test in the module."""
    parse_call_method_name.cache_clear()


def test_single_int_arg():
    expected = ("set_name", (1,), {})
    actual = parse_call_method_name("set_name(1)")

    assert actual == expected


def test_single_dict_arg():
    expected = ("set_name", ({"1": 2, "3": 4},), {})
    actual = parse_call_method_name('set_name({"1": 2, "3": 4})')

    assert actual == expected


def test_multiple_args():
    expected = ("set_name", (0, {"1": 2}), {})
    actual = parse_call_method_name('set_name(0, {"1": 2})')

    assert actual == expected


def test_multiple_args_2():
    expected = ("set_name", (1, 2), {})
    actual = parse_call_method_name("set_name(1, 2)")

    assert actual == expected


def test_var_with_curly_braces():
    expected = (
        "set_name",
        ("{}",),
        {},
    )
    actual = parse_call_method_name('set_name("{}")')

    assert actual == expected


def test_one_arg():
    expected = (
        "set_name",
        ("1",),
        {},
    )
    actual = parse_call_method_name('set_name("1")')

    assert actual == expected


def test_kwargs():
    expected = ("set_name", (), {"kwarg1": "wow"})
    actual = parse_call_method_name("set_name(kwarg1='wow')")

    assert actual == expected


def test_args_and_kwargs():
    expected = ("set_name", (8, 9), {"kwarg1": "wow"})
    actual = parse_call_method_name("set_name(8, 9, kwarg1='wow')")

    assert actual == expected


def test_special_method_without_parens():
    expected = ("$reset", (), {})
    actual = parse_call_method_name("$reset")

    assert actual == expected


def test_special_method_with_parens():
    expected = ("$reset", (), {})
    actual = parse_call_method_name("$reset()")

    assert actual == expected
