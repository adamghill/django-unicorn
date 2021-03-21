import pytest

from django_unicorn.components import UnicornView
from django_unicorn.db import DbModel
from django_unicorn.decorators import db_model
from django_unicorn.errors import UnicornCacheError
from django_unicorn.utils import get_cacheable_component
from example.coffee.models import Flavor


class FakeComponent(UnicornView):
    something = 0

    @db_model
    def get_pk(self, flavor, something):
        self.something = something
        return flavor.pk

    class Meta:
        db_models = [DbModel("flavor", Flavor)]


@pytest.fixture
def component():
    return FakeComponent(component_id="asdf", component_name="faker")


@pytest.mark.django_db
def test_happy_path(component):
    flavor = Flavor()
    flavor.save()

    pk = component.get_pk({"name": "flavor", "pk": flavor.pk}, 1)
    assert pk == flavor.pk
    assert 1 == component.something


@pytest.mark.django_db
def test_missing_name(component):
    with pytest.raises(AssertionError):
        component.get_pk({"pk": 1}, 1)


@pytest.mark.django_db
def test_missing_pk(component):
    with pytest.raises(AssertionError):
        component.get_pk({"name": "flavor"}, 1)


@pytest.mark.django_db
def test_model_not_found(component):
    with pytest.raises(Flavor.DoesNotExist):
        component.get_pk({"name": "flavor", "pk": -99}, 1)


@pytest.mark.django_db
def test_no_meta():
    class FakeComponentWithNoMeta(UnicornView):
        @db_model
        def get_pk(self, flavor):
            return flavor.pk

    component = FakeComponentWithNoMeta(component_id="asdf", component_name="faker")

    with pytest.raises(AssertionError):
        component.get_pk({"name": "flavor", "pk": -99})


@pytest.mark.django_db
def test_missing_db_models():
    class FakeComponentWithNoDbModels(UnicornView):
        @db_model
        def get_pk(self, flavor):
            return flavor.pk

        class Meta:
            db_models = []

    component = FakeComponentWithNoDbModels(component_id="asdf", component_name="faker")

    with pytest.raises(AssertionError):
        component.get_pk({"name": "flavor", "pk": -99})


@pytest.mark.django_db
def test_component_db_model_is_pickleable(component):
    """
    Using the `wrapt` library would raise an exception, but the `decorator` library
    is pickleable, so this should be a-ok
    """
    get_cacheable_component(component)
