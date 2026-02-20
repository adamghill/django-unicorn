from django_unicorn.typer import get_type_hints


class Parent:
    name: str


class Child(Parent):
    age: int


def test_get_type_hints_inheritance():
    """
    Verify that get_type_hints returns type hints from parent classes
    when called with an instance of a subclass.
    """
    instance = Child()
    type_hints = get_type_hints(instance)

    assert "name" in type_hints
    assert type_hints["name"] is str
    assert "age" in type_hints
    assert type_hints["age"] is int


if __name__ == "__main__":
    test_get_type_hints_inheritance()
