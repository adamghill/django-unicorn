import pytest

from django_unicorn.typer import _construct_model
from example.books.models import Author, Book
from example.coffee.models import Flavor


def test_construct_model_simple_model():
    model_data = {
        "pk": 1,
        "name": "test-name",
    }

    actual = _construct_model(Flavor, model_data)

    assert actual.pk == 1
    assert actual.name == "test-name"


@pytest.mark.django_db
def test_construct_model_foreign_key():
    flavor = Flavor(name="first-flavor")
    flavor.save()
    parent = Flavor(name="parent-flavor")
    parent.save()

    model_data = {
        "pk": flavor.id,
        "name": flavor.name,
        "parent": parent.id,
    }

    actual = _construct_model(Flavor, model_data)

    assert actual.pk == flavor.pk
    assert actual.name == flavor.name
    assert actual.parent.pk == parent.pk
    assert actual.parent.name == parent.name


@pytest.mark.django_db
@pytest.mark.skip("This test isn't all that helpful unless related models get serialized")
def test_construct_model_recursive_foreign_key():
    flavor = Flavor(name="first-flavor")
    flavor.save()
    parent = Flavor(name="parent-flavor")
    parent.save()

    model_data = {
        "pk": flavor.pk,
        "name": flavor.name,
        "parent": parent.pk,
    }

    actual = _construct_model(Flavor, model_data)

    assert actual.pk == flavor.pk
    assert actual.name == flavor.name
    assert actual.parent.pk == parent.pk
    assert actual.parent.name == parent.name


@pytest.mark.django_db
def test_construct_model_many_to_many():
    author = Author(name="author 1")
    author.save()
    book = Book(title="book 1", date_published="2021-01-01")
    book.save()
    author.books.add(book)

    author_data = {
        "pk": author.pk,
        "name": author.name,
        "books": [
            book.pk,
        ],
    }

    actual = _construct_model(Author, author_data)

    assert actual.pk == author.pk
    assert actual.name == author.name
    assert actual.books.count() == 1
    assert actual.books.all()[0].title == book.title
