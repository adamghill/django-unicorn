from django_unicorn.components import UnicornView
from django_unicorn.views.utils import _is_component_field_model_or_unicorn_field
from example.coffee.models import Flavor


class TypeHintView(UnicornView):
    model: Flavor = None


class ModelInstanceView(UnicornView):
    model = Flavor()


def test_type_hint():
    component = TypeHintView(component_name="asdf", component_id="test_type_hint")
    name = "model"
    actual = _is_component_field_model_or_unicorn_field(component, name)

    assert actual
    assert component.model is not None
    assert type(component.model) is Flavor


def test_model_instance():
    component = ModelInstanceView(component_name="asdf", component_id="test_model_instance")
    name = "model"
    actual = _is_component_field_model_or_unicorn_field(component, name)

    assert actual
    assert component.model is not None
    assert type(component.model) is Flavor
