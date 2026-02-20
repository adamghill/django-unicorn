from django.db import models


class Book(models.Model):
    TYPES = ((1, "Hardcover"), (2, "Softcover"))
    title = models.CharField(max_length=255)
    date_published = models.DateField()
    type = models.IntegerField(choices=TYPES, default=1)


class Author(models.Model):
    name = models.CharField(max_length=1024)
    books = models.ManyToManyField(Book)
