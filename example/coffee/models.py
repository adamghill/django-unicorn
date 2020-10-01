from django.db.models import Model, ForeignKey, SET_NULL
from django.db.models.fields import CharField


class Flavor(Model):
    name = CharField(max_length=255)
    label = CharField(max_length=255)
    parent = ForeignKey("self", blank=True, null=True, on_delete=SET_NULL)

    def __str__(self):
        return self.name
