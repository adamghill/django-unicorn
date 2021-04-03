from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    date_published = models.DateField()


class Author(models.Model):
    name = models.CharField(max_length=1024)
    books = models.ManyToManyField(Book)
