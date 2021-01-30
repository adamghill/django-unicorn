from django_unicorn.components import convert_to_pascal_case


def test_convert_to_pascal_case():
    expected = "HelloWorld"
    actual = convert_to_pascal_case("hello-world")

    assert expected == actual
