from django_unicorn.components.unicorn_view import convert_to_dash_case


def test_convert_to_dash_case():
    expected = "hello-world"
    actual = convert_to_dash_case("hello_world")

    assert expected == actual
