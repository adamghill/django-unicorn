from django.db.models import Model
from django.db.models.fields import CharField

from django_unicorn.components import UnicornView
from django_unicorn.views.utils import set_property_from_data


class FakeModel(Model):
    name = CharField(max_length=255)

    class Meta:
        app_label = "www"


class ModelPropertyView(UnicornView):
    model = FakeModel(name="fake_model")


def test_set_property_from_data_model():
    component = ModelPropertyView(component_name="test", component_id="test_set_property_from_data_model")
    assert "fake_model" == component.model.name

    set_property_from_data(component, "model", {"name": "fake_model_updated"})

    assert "fake_model_updated" == component.model.name
