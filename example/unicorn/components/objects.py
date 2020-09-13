from datetime import datetime

from django_unicorn.components import UnicornView, UnicornField

from books.models import Book

from django.utils.timezone import now


class PublishDateField(UnicornField):
    def __init__(self, year):
        self.year = year


class BookField(UnicornField):
    def __init__(self):
        self.title = "Neverwhere"
        self.publish_date_field = PublishDateField(year=1996)
        self.publish_date = datetime(1996, 9, 16)


class ObjectsView(UnicornView):
    unicorn_field = BookField()
    dictionary = {"name": "dictionary", "nested": {"name": "nested dictionary"}}
    book = Book(title="The Sandman")
    books = Book.objects.all()

    date_example = now()

    def get_date(self):
        self.date_example = now()

    def set_dictionary(self, val):
        self.dictionary = val
