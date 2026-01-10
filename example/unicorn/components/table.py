# -*- coding: utf-8 -*-

from example.books.models import Book, Author
from django_unicorn.components import UnicornView
from typing import Any, cast

class TableView(UnicornView):
    books = Book.objects.none()

    def mount(self):
        self.load_table()

    def load_table(self):
        print(Book.objects.all())
        if Book.objects.count() == 0:
            for author, title in [
                ("Dr. Seuss", "The Cat in the Hat"),
                ("J.K. Rowling", "Harry Potter and the Philosopher's Stone"),
                ("Roald Dahl", "Matilda"),
                ("Maurice Sendak", "Where the Wild Things Are"),
                ("A.A. Milne", "Winnie the Pooh")
            ]:
                author = Author(name=author).save()
                Book(author=author, title=title).save()

        self.books = Book.objects.all()

        for child in self.children:
            if hasattr(child, "is_editing"):
                cast(Any, child).is_editing = False
