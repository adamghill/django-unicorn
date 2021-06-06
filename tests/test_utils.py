from django_unicorn.utils import (
    generate_checksum,
    get_method_arguments,
    get_type_hints,
    sanitize_html,
)


def test_generate_checksum_bytes(settings):
    settings.SECRET_KEY = "asdf"

    expected = "TfxFqcQL"
    actual = generate_checksum(b'{"name": "test"}')

    assert expected == actual


def test_generate_checksum_str(settings):
    settings.SECRET_KEY = "asdf"

    expected = "TfxFqcQL"
    actual = generate_checksum('{"name": "test"}')

    assert expected == actual


def test_get_method_arguments():
    def test_func(input_str):
        return input_str

    expected = [
        "input_str",
    ]
    actual = get_method_arguments(test_func)
    assert actual == expected


def test_get_method_arguments_with_type_annotation():
    def test_func(input_str: str):
        return input_str

    expected = [
        "input_str",
    ]
    actual = get_method_arguments(test_func)
    assert actual == expected


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


def test_sanitize_html():
    expected = '{"id":"abcd123","name":"text-inputs","key":"asdf","data":{"name":"World","testing_thing":"Whatever \\u003C/script\\u003E \\u003Cscript\\u003Ealert(\'uh oh\')\\u003C/script\\u003E"},"calls":[],"hash":"hjkl"}'
    data = '{"id":"abcd123","name":"text-inputs","key":"asdf","data":{"name":"World","testing_thing":"Whatever </script> <script>alert(\'uh oh\')</script>"},"calls":[],"hash":"hjkl"}'
    actual = sanitize_html(data)
    assert actual == expected
