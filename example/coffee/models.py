import uuid

from django.db.models import SET_NULL, ForeignKey, Model
from django.db.models.fields import (
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    DurationField,
    FloatField,
    TimeField,
    UUIDField,
)


class Flavor(Model):
    name = CharField(max_length=255)
    label = CharField(max_length=255)
    parent = ForeignKey("self", blank=True, null=True, on_delete=SET_NULL)
    float_value = FloatField(blank=True, null=True)
    decimal_value = DecimalField(blank=True, null=True, max_digits=10, decimal_places=2)
    uuid = UUIDField(default=uuid.uuid4)
    datetime = DateTimeField(blank=True, null=True)
    date = DateField(blank=True, null=True)
    time = TimeField(blank=True, null=True)
    duration = DurationField(blank=True, null=True)

    def __str__(self):
        return self.name
