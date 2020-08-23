from django.db.models import Model
from django.db.models.fields import CharField, DateField


class Book(Model):
    title = CharField(max_length=255)
    date_published = DateField()
