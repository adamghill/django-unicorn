import pytest

from django_unicorn.components.unicorn_view import UnicornView
from django_unicorn.errors import ComponentModuleLoadError


def test_no_component():
    with pytest.raises(ComponentModuleLoadError) as e:
        UnicornView.create(component_id="create-no-component", component_name="create-no-component")

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentModuleLoadError: The component module 'create_no_component' could not be loaded."  # noqa: E501
    )


class FakeComponent(UnicornView):
    pass


def test_components_settings(settings):
    settings.UNICORN["COMPONENTS"] = {"create-components-setting": FakeComponent}

    component = UnicornView.create(
        component_id="create-components-setting-id", component_name="create-components-setting"
    )
    assert component
