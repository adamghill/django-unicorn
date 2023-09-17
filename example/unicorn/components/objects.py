from datetime import datetime, timedelta
from decimal import Decimal as D
from enum import Enum
from typing import List, Optional

from django.utils.timezone import now

from pydantic import BaseModel

from django_unicorn.components import UnicornField, UnicornView
from example.books.models import Book


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class PublishDateField(UnicornField):
    def __init__(self, year):
        self.year = year


class BookField(UnicornField):
    def __init__(self):
        self.title = "Neverwhere"
        self.publish_date_field = PublishDateField(year=1996)
        self.publish_date = datetime(1996, 9, 16)


class PydanticBook(BaseModel):
    title = "American Gods"
    publish_date: Optional[datetime] = datetime(1996, 9, 16)


class ObjectsView(UnicornView):
    unicorn_field = BookField()
    pydantic_field = PydanticBook()
    dictionary = {"name": "dictionary", "nested": {"name": "nested dictionary"}}
    dictionary_2 = {"5": "a", "9": "b"}
    book = Book(title="The Sandman")
    books = Book.objects.all()
    date_example = now()
    date_example_with_typehint: datetime = now()
    dates_with_no_typehint = []
    dates_with_old_typehint: List[datetime] = []
    dates_with_new_typehint: list[datetime] = []
    dates_with_list_typehint: list = []
    float_example: float = 1.1
    decimal_example = D("1.1")
    int_example = 4
    color = Color.RED

    def mount(self):
        self.dates_with_no_typehint = [datetime(2021, 1, 1), datetime(2021, 1, 2)]
        self.dates_with_old_typehint = [datetime(2022, 2, 1), datetime(2022, 2, 2)]
        self.dates_with_new_typehint = [datetime(2023, 3, 1), datetime(2023, 3, 2)]
        self.dates_with_list_typehint = [datetime(2024, 4, 1), datetime(2024, 4, 2)]

    def get_date(self):
        self.date_example = now()

    def check_date(self, dt: datetime):
        assert type(dt) is datetime

        self.date_example = dt

    def add_hour(self):
        self.date_example_with_typehint = self.date_example_with_typehint + timedelta(hours=1)

    def set_dictionary(self, val):
        self.dictionary = val

    def set_dictionary_2(self):
        self.dictionary_2["1"] = "c"
        self.dictionary_2["6"] = "d"
        self.dictionary_2["11"] = "e"

    def add_one_to_float(self):
        self.float_example += 1

    def set_color(self, color: int):
        self.color = Color(color)
