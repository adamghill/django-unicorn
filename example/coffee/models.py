from django.db.models import SET_NULL, ForeignKey, Model
from django.db.models.fields import CharField, DateTimeField, DecimalField, FloatField


class Flavor(Model):
    name = CharField(max_length=255)
    label = CharField(max_length=255)
    parent = ForeignKey("self", blank=True, null=True, on_delete=SET_NULL)
    float_value = FloatField(null=True)
    decimal_value = DecimalField(null=True, max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Bean(Model):
    name = CharField(max_length=255, unique=True)
    created = DateTimeField(auto_now_add=True, editable=False)
    last_updated = DateTimeField(auto_now=True, editable=False)
