from django_unicorn.components.unicorn_view import convert_to_snake_case


def test_convert_to_snake_case():
    expected = "hello_world"
    actual = convert_to_snake_case("hello-world")

    assert expected == actual
