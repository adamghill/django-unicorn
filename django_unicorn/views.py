import logging
from functools import wraps
from typing import Any, Dict, List, Union

from django.db.models import Model
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import orjson
from bs4 import BeautifulSoup

from .call_method_parser import InvalidKwarg, parse_call_method_name, parse_kwarg
from .components import UnicornField, UnicornView
from .decorators import timed
from .errors import UnicornViewError
from .message import ComponentRequest, Return
from .serializer import loads
from .utils import generate_checksum


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def handle_error(view_func):
    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except UnicornViewError as e:
            return JsonResponse({"error": str(e)})
        except AssertionError as e:
            return JsonResponse({"error": str(e)})

    return wraps(view_func)(wrapped_view)


@timed
def _set_property_from_data(
    component_or_field: Union[UnicornView, UnicornField, Model], name: str, value,
) -> None:
    """
    Sets properties on the component based on passed-in data.
    """

    if hasattr(component_or_field, name):
        field = getattr(component_or_field, name)

        # UnicornField and Models are always a dictionary (can be nested)
        if isinstance(field, UnicornField) or isinstance(field, Model):
            if isinstance(value, dict):
                for key in value.keys():
                    key_value = value[key]
                    _set_property_from_data(field, key, key_value)
            else:
                _set_property_from_data(field, field.name, value)
        else:
            if hasattr(component_or_field, "_set_property"):
                # Can assume that `component_or_field` is a component
                component_or_field._set_property(name, value)
            else:
                setattr(component_or_field, name, value)


@timed
def _set_property_value(
    component: UnicornView, property_name: str, property_value: Any, data: Dict = {}
) -> None:
    """
    Sets properties on the component.
    Also updates the data dictionary which gets set back as part of the payload.

    Args:
        param component: Component to set attributes on.
        param property_name: Name of the property.
        param property_value: Value to set on the property.
        param data: Dictionary that gets sent back with the response. Defaults to {}.
    """

    assert property_name is not None, "Property name is required"
    assert property_value is not None, "Property value is required"

    component.updating(property_name, property_value)

    """
    Handles nested properties. For example, for the following component:

    class Author(UnicornField):
        name = "Neil"

    class TestView(UnicornView):
        author = Author()
    
    `payload` would be `{'name': 'author.name', 'value': 'Neil Gaiman'}`

    The following code updates UnicornView.author.name based the payload's `author.name`.
    """
    property_name_parts = property_name.split(".")
    component_or_field = component
    data_or_dict = data  # Could be an internal portion of data that gets set

    for (idx, property_name_part) in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                if hasattr(component_or_field, "_set_property"):
                    # Can assume that `component_or_field` is a component
                    component_or_field._set_property(property_name_part, property_value)
                else:
                    # Handle calling the updating/updated method for nested properties
                    property_name_snake_case = property_name.replace(".", "_")
                    updating_function_name = f"updating_{property_name_snake_case}"
                    updated_function_name = f"updated_{property_name_snake_case}"

                    if hasattr(component, updating_function_name):
                        getattr(component, updating_function_name)(property_value)

                    setattr(component_or_field, property_name_part, property_value)

                    if hasattr(component, updated_function_name):
                        getattr(component, updated_function_name)(property_value)

                data_or_dict[property_name_part] = property_value
            else:
                component_or_field = getattr(component_or_field, property_name_part)
                data_or_dict = data_or_dict.get(property_name_part, {})
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                component_or_field[property_name_part] = property_value
                data_or_dict[property_name_part] = property_value
            else:
                component_or_field = component_or_field[property_name_part]
                data_or_dict = data_or_dict.get(property_name_part, {})

    component.updated(property_name, property_value)


@timed
def _get_property_value(component: UnicornView, property_name: str) -> Any:
    """
    Gets property value from the component based on the property name.
    Handles nested property names.

    Args:
        param component: Component to get property values from.
        param property_name: Property name. Can be "dot-notation" to get nested properties.
    """

    assert property_name is not None, "property_name name is required"

    # Handles nested properties
    property_name_parts = property_name.split(".")
    component_or_field = component

    for (idx, property_name_part) in enumerate(property_name_parts):
        if hasattr(component_or_field, property_name_part):
            if idx == len(property_name_parts) - 1:
                return getattr(component_or_field, property_name_part)
            else:
                component_or_field = getattr(component_or_field, property_name_part)
        elif isinstance(component_or_field, dict):
            if idx == len(property_name_parts) - 1:
                return component_or_field[property_name_part]
            else:
                component_or_field = component_or_field[property_name_part]


@timed
def _call_method_name(
    component: UnicornView, method_name: str, params: List[Any]
) -> Any:
    """
    Calls the method name with parameters.

    Args:
        param component: Component to call method on.
        param method_name: Method name to call.
        param params: List of arguments for the method.
    """

    if method_name is not None and hasattr(component, method_name):
        func = getattr(component, method_name)

        if params:
            return func(*params)
        else:
            return func()


@timed
@handle_error
@csrf_protect
@require_POST
def message(request: HttpRequest, component_name: str = None) -> JsonResponse:
    """
    Endpoint that instantiates the component and does the correct action
    (set an attribute or call a method) depending on the JSON payload in the body.

    Args:
        param request: HttpRequest for the function-based view.
        param: component_name: Name of the component, e.g. "hello-world".
    
    Returns:
        JSON with the following structure:
        {
            "id": component_id,
            "dom": html,  // re-rendered version of the component after actions in the payload are completed
            "data": {},  // updated data after actions in the payload are completed
        }
    """

    assert component_name, "Missing component name in url"

    component_request = ComponentRequest(request)
    component = UnicornView.create(
        component_id=component_request.id,
        component_name=component_name,
        request=request,
    )
    validate_all_fields = False

    # Get a copy of the data passed in to determine what fields are updated later
    original_data = component_request.data.copy()

    # Set component properties based on request data
    for (property_name, property_value) in component_request.data.items():
        _set_property_from_data(component, property_name, property_value)
    component.hydrate()

    is_reset_called = False
    return_data = None
    partials = []

    for action in component_request.action_queue:
        action_type = action.get("type")
        payload = action.get("payload", {})
        partials.append(action.get("partial"))

        if action_type == "syncInput":
            property_name = payload.get("name")
            property_value = payload.get("value")
            _set_property_value(
                component, property_name, property_value, component_request.data
            )
        elif action_type == "dbInput":
            model = payload.get("model")
            db = payload.get("db", {})
            db_model_name = db.get("name")
            pk = db.get("pk")

            DbModel = None
            db_defaults = {}

            if model:
                model_class = getattr(component, model)

                if hasattr(model_class, "model"):
                    DbModel = model_class.model

                    if hasattr(component, "Meta"):
                        for m in component.Meta.db_models:
                            if m.model_class == model_class.model:
                                db_defaults = m.defaults
                                break

            if not DbModel and db_model_name:
                assert hasattr(component, "Meta") and hasattr(
                    component.Meta, "db_models"
                ), f"Missing Meta.db_models list in component"

                for m in component.Meta.db_models:
                    if m.name == db_model_name:
                        DbModel = m.model_class
                        db_defaults = m.defaults
                        break

            fields = payload.get("fields", {})

            assert (
                DbModel
            ), f"Missing {model}.model and {db_model_name} in Meta.db_models"
            assert issubclass(
                DbModel, Model
            ), "Model must be an instance of `django.db.models.Model"

            if fields:
                fields_to_update = db_defaults
                fields_to_update.update(fields)

                if pk:
                    DbModel.objects.filter(pk=pk).update(**fields_to_update)
                else:
                    instance = DbModel(**fields_to_update)
                    instance.save()
                    pk = instance.pk
        elif action_type == "callMethod":
            call_method_name = payload.get("name", "")
            assert call_method_name, "Missing 'name' key for callMethod"

            (method_name, params) = parse_call_method_name(call_method_name)
            return_data = Return(method_name, params)
            setter_method = {}

            if "=" in call_method_name:
                try:
                    setter_method = parse_kwarg(
                        call_method_name, raise_if_unparseable=True
                    )
                except InvalidKwarg:
                    pass

            if setter_method:
                property_name = list(setter_method.keys())[0]
                property_value = setter_method[property_name]

                _set_property_value(component, property_name, property_value)
                return_data = Return(property_name, [property_value])
            else:
                if method_name == "$refresh":
                    # Handle the refresh special action
                    component = UnicornView.create(
                        component_id=component_request.id,
                        component_name=component_name,
                        use_cache=True,
                        request=request,
                    )
                elif method_name == "$reset":
                    # Handle the reset special action
                    component = UnicornView.create(
                        component_id=component_request.id,
                        component_name=component_name,
                        use_cache=False,
                        request=request,
                    )

                    #  Explicitly remove all errors and prevent validation from firing before render()
                    component.errors = {}
                    is_reset_called = True
                elif method_name == "$toggle":
                    for property_name in params:
                        property_value = _get_property_value(component, property_name)
                        property_value = not property_value

                        _set_property_value(component, property_name, property_value)
                elif method_name == "$validate":
                    # Handle the validate special action
                    validate_all_fields = True
                else:
                    component.calling(method_name, params)
                    return_data.value = _call_method_name(
                        component, method_name, params
                    )
                    component.called(method_name, params)
        else:
            raise UnicornViewError(f"Unknown action_type '{action_type}'")

    # Re-load frontend context variables to deal with non-serializable properties
    component_request.data = orjson.loads(component.get_frontend_context_variables())

    if not is_reset_called:
        if validate_all_fields:
            component.validate()
        else:
            model_names_to_validate = []

            for key, value in original_data.items():
                if value != component_request.data.get(key):
                    model_names_to_validate.append(key)

            component.validate(model_names=model_names_to_validate)

    rendered_component = component.render()
    partial_doms = []

    if partials and all(partials):
        soup = BeautifulSoup(rendered_component, features="html.parser")

        for partial in partials:
            partial_found = False
            only_id = False
            only_key = False

            target = partial.get("target")

            if not target:
                target = partial.get("key")

                if target:
                    only_key = True

            if not target:
                target = partial.get("id")

                if target:
                    only_id = True

            assert target, "Partial target is required"

            if not only_id:
                for element in soup.find_all():
                    if (
                        "unicorn:key" in element.attrs
                        and element.attrs["unicorn:key"] == target
                    ):
                        partial_doms.append({"key": target, "dom": str(element)})
                        partial_found = True
                        break

            if not partial_found and not only_key:
                for element in soup.find_all():
                    if "id" in element.attrs and element.attrs["id"] == target:
                        partial_doms.append({"id": target, "dom": str(element)})
                        partial_found = True
                        break

    res = {
        "id": component_request.id,
        "data": component_request.data,
        "errors": component.errors,
        "checksum": generate_checksum(orjson.dumps(component_request.data)),
    }

    if partial_doms:
        res.update({"partials": partial_doms})
    else:
        res.update({"dom": rendered_component})

    if return_data:
        res.update(
            {"return": return_data.get_data(),}
        )

        if return_data.redirect:
            res.update(
                {"redirect": return_data.redirect,}
            )

        if return_data.poll:
            res.update(
                {"poll": return_data.poll,}
            )

    parent_component = component.parent

    if parent_component:
        parent_frontend_context_variables = (
            parent_component.get_frontend_context_variables()
        )

        parent_dom = parent_component.render()

        soup = BeautifulSoup(parent_dom, features="html.parser")
        checksum = None

        # TODO: This doesn't create the same checksum for some reason
        # checksum = orjson.dumps(parent_frontend_context_variables)

        for element in soup.find_all():
            if "unicorn:checksum" in element.attrs:
                checksum = element["unicorn:checksum"]
                break

        res.update(
            {
                "parent": {
                    "id": parent_component.component_id,
                    "dom": parent_dom,
                    "checksum": checksum,
                    "data": loads(parent_frontend_context_variables),
                    "errors": parent_component.errors,
                }
            }
        )

    return JsonResponse(res)
