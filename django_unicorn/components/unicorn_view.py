import importlib
import inspect
import logging
import pickle
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.http import HttpRequest
from django.views.generic.base import TemplateView

from cachetools.lru import LRUCache

from django_unicorn.settings import get_cache_alias

from .. import serializer
from ..decorators import timed
from ..errors import ComponentLoadError, UnicornCacheError
from ..settings import get_setting
from ..utils import get_cacheable_component
from .fields import UnicornField
from .unicorn_template_response import UnicornTemplateResponse


logger = logging.getLogger(__name__)


# TODO: Make maxsize configurable
location_cache = LRUCache(maxsize=100)

# Module cache to store the found component class by id
views_cache = LRUCache(maxsize=100)

# Module cache for constructed component classes
# This can create a subtle race condition so a more long-term solution needs to be found
constructed_views_cache = LRUCache(maxsize=100)
COMPONENTS_MODULE_CACHE_ENABLED = "pytest" not in sys.modules


def convert_to_snake_case(s: str) -> str:
    # TODO: Better handling of dash->snake
    return s.replace("-", "_")


def convert_to_pascal_case(s: str) -> str:
    # TODO: Better handling of dash/snake->pascal-case
    s = convert_to_snake_case(s)
    return "".join(word.title() for word in s.split("_"))


def get_locations(component_name):
    locations = []

    if "." in component_name:
        # Handle component names that specify a folder structure
        component_name = component_name.replace("/", ".")

        # Handle fully-qualified component names (e.g. `project.unicorn.HelloWorldView`)
        class_name = component_name.split(".")[-1:][0]
        module_name = component_name.replace("." + class_name, "")
        locations.append((class_name, module_name))

        # Assume if it ends with "View", then we don't need to add other
        if component_name.endswith("View") or component_name.endswith("Component"):
            return locations

    # Handle component names that specify a folder structure
    component_name = component_name.replace("/", ".")

    # Use conventions to find the component class
    class_name = convert_to_pascal_case(component_name)

    if "." in class_name:
        if class_name.split(".")[-1:]:
            class_name = class_name.split(".")[-1:][0]

    class_name = f"{class_name}View"
    module_name = convert_to_snake_case(component_name)

    unicorn_apps = get_setting("APPS", settings.INSTALLED_APPS)

    assert (
        isinstance(unicorn_apps, list)
        or isinstance(unicorn_apps, tuple)
        or isinstance(unicorn_apps, set)
    ), "APPS is expected to be a list, tuple or set"

    for app in unicorn_apps:
        # Handle an installed app that actually points to an app config
        if ".apps." in app:
            app_config_idx = app.index(".apps.")
            app = app[:app_config_idx]

        app_module_name = f"{app}.components.{module_name}"
        locations.append((class_name, app_module_name))

    return locations


@timed
def construct_component(
    component_class,
    component_id,
    component_name,
    component_key,
    parent,
    request,
    **kwargs,
):
    """
    Constructs a class instance.
    """
    component = component_class(
        component_id=component_id,
        component_name=component_name,
        component_key=component_key,
        parent=parent,
        request=request,
        **kwargs,
    )

    component.calls = []
    component.children = []
    component._children_set = False

    component.mount()
    component.hydrate()
    component.complete()
    component._validate_called = False

    return component


class UnicornView(TemplateView):
    response_class = UnicornTemplateResponse
    component_name: str = ""
    component_key: str = ""
    request = None
    parent = None
    children = []

    # Caches to reduce the amount of time introspecting the class
    _methods_cache: Dict[str, Callable] = {}
    _attribute_names_cache: List[str] = []
    _hook_methods_cache: List[str] = []

    # Dictionary with key: attribute name; value: pickled attribute value
    _resettable_attributes_cache: Dict[str, Any] = {}

    # JavaScript method calls
    calls = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        assert self.component_name, "Component name is required"

        if "id" in kwargs and kwargs["id"]:
            # Sometimes the component_id is initially in kwargs["id"]
            self.component_id = kwargs["id"]

        assert hasattr(self, "component_id"), "Component id is required"
        assert self.component_id, "Component id is required"
        self.component_cache_key = f"unicorn:component:{self.component_id}"

        if "request" in kwargs:
            self.setup(kwargs["request"])

        if "parent" in kwargs:
            self.parent = kwargs["parent"]

        self._init_script: str = ""
        self._children_set = False
        self._validate_called = False
        self.errors = {}
        self._set_default_template_name()
        self._set_caches()

    @timed
    def _set_default_template_name(self) -> None:
        """
        Sets a default template name based on component's name if necessary.
        """
        get_template_names_is_valid = False

        try:
            # Check for get_template_names by explicitly calling it since it
            # is defined in TemplateResponseMixin, but can throw ImproperlyConfigured.
            self.get_template_names()
            get_template_names_is_valid = True
        except ImproperlyConfigured:
            pass

        if not self.template_name and not get_template_names_is_valid:
            # Convert component name with a dot to a folder structure
            template_name = self.component_name.replace(".", "/")
            self.template_name = f"unicorn/{template_name}.html"

    @timed
    def _set_caches(self) -> None:
        """
        Setup some initial "caches" to prevent Python from having to introspect
        a component UnicornView for methods and properties multiple times.
        """
        self._attribute_names_cache = self._attribute_names()
        self._set_hook_methods_cache()
        self._methods_cache = self._methods()
        self._set_resettable_attributes_cache()

    @timed
    def reset(self):
        for (
            attribute_name,
            pickled_value,
        ) in self._resettable_attributes_cache.items():
            try:
                attribute_value = pickle.loads(pickled_value)
                self._set_property(attribute_name, attribute_value)
            except TypeError:
                logger.warn(
                    f"Resetting '{attribute_name}' attribute failed because it could not be constructed."
                )
                pass
            except pickle.PickleError:
                logger.warn(
                    f"Resetting '{attribute_name}' attribute failed because it could not be de-pickled."
                )
                pass

    def call(self, function_name, *args):
        """
        Add a JavaScript method name and arguments to be called after the component is rendered.
        """
        self.calls.append({"fn": function_name, "args": args})

    def mount(self):
        """
        Hook that gets called when the component is first created.
        """
        pass

    def hydrate(self):
        """
        Hook that gets called when the component's data is hydrated.
        """
        pass

    def complete(self):
        """
        Hook that gets called after all component methods are executed.
        """
        pass

    def rendered(self, html):
        """
        Hook that gets called after the component has been rendered.
        """
        pass

    def parent_rendered(self, html):
        """
        Hook that gets called after the component's parent has been rendered.
        """
        pass

    def updating(self, name, value):
        """
        Hook that gets called when a component's data is about to get updated.
        """
        pass

    def updated(self, name, value):
        """
        Hook that gets called when a component's data is updated.
        """
        pass

    def calling(self, name, args):
        """
        Hook that gets called when a component's method is about to get called.
        """
        pass

    def called(self, name, args):
        """
        Hook that gets called when a component's method is called.
        """
        pass

    @timed
    def render(self, init_js=False) -> str:
        """
        Renders a UnicornView component with the public properties available. Delegates to a
        UnicornTemplateResponse to actually render a response.
 
        Args:
            param init_js: Whether or not to include the Javascript required to initialize the component.
        """

        response = self.render_to_response(
            context=self.get_context_data(), component=self, init_js=init_js,
        )

        # render_to_response() could only return a HttpResponse, so check for render()
        if hasattr(response, "render"):
            response.render()

        rendered_component = response.content.decode("utf-8")

        # Set the current component as a child of the parent if there is a parent
        # If no parent, mark that the component has its children set.
        # This works because the nested (internal) components get rendered first before the parent,
        # so once we hit a component without a parent we know all of the children have been rendered correctly
        # TODO: This might fall apart with a third layer of nesting components
        if self.parent:
            if not self.parent._children_set:
                self.parent.children.append(self)
        else:
            self._children_set = True

        return rendered_component

    @timed
    def get_frontend_context_variables(self) -> str:
        """
        Get publicly available properties and output them in a string-encoded JSON object.
        """

        frontend_context_variables = {}
        attributes = self._attributes()
        frontend_context_variables.update(attributes)

        # Remove any field in `javascript_exclude` from the `frontend_context_variables`
        if hasattr(self, "Meta") and hasattr(self.Meta, "javascript_exclude"):
            if isinstance(self.Meta.javascript_exclude, Sequence):
                for field_name in self.Meta.javascript_exclude:
                    if field_name in frontend_context_variables:
                        del frontend_context_variables[field_name]

        # Add cleaned values to `frontend_content_variables` based on the widget in form's fields
        form = self._get_form(attributes)

        if form:
            form.is_valid()

            for key in attributes.keys():
                if key in form.fields:
                    field = form.fields[key]

                    if key in form.cleaned_data:
                        cleaned_value = form.cleaned_data[key]
                        value = field.widget.format_value(cleaned_value)

                        # Don't update the frontend variable if the only change is
                        # stripping off the whitespace from the field value
                        # https://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.CharField.strip
                        if (
                            not hasattr(frontend_context_variables[key], "strip")
                            or frontend_context_variables[key].strip() != value
                        ):
                            frontend_context_variables[key] = value

        encoded_frontend_context_variables = serializer.dumps(
            frontend_context_variables
        )

        return encoded_frontend_context_variables

    @timed
    def _get_form(self, data):
        if hasattr(self, "form_class"):
            try:
                form = self.form_class(data)
                form.is_valid()

                return form
            except Exception as e:
                logger.exception(e)

    @timed
    def get_context_data(self, **kwargs):
        """
        Overrides the standard `get_context_data` to add in publicly available
        properties and methods.
        """

        context = super().get_context_data(**kwargs)

        attributes = self._attributes()
        context.update(attributes)
        context.update(self._methods())
        context.update({"unicorn": {"errors": self.errors}})

        return context

    @timed
    def is_valid(self, model_names: List = None) -> bool:
        return len(self.validate(model_names).keys()) == 0

    @timed
    def validate(self, model_names: List = None) -> Dict:
        """
        Validates the data using the `form_class` set on the component.

        Args:
            model_names: Only include validation errors for specified fields. If none, validate everything.
        """
        # TODO: Handle form.non_field_errors()?

        if self._validate_called:
            return self.errors

        self._validate_called = True

        data = self._attributes()
        form = self._get_form(data)

        if form:
            form_errors = form.errors.get_json_data(escape_html=True)

            # This code is confusing, but handles this use-case:
            # the component has two models, one that starts with an error and one
            # that is valid. Validating the valid one should not show an error for
            # the invalid one. Only after the invalid field is updated, should the
            # error show up and persist, even after updating the valid form.
            if self.errors:
                keys_to_remove = []

                for key, value in self.errors.items():
                    if key in form_errors:
                        self.errors[key] = value
                    else:
                        keys_to_remove.append(key)

                for key in keys_to_remove:
                    self.errors.pop(key)

            if model_names is not None:
                for key, value in form_errors.items():
                    if key in model_names:
                        self.errors[key] = value
            else:
                self.errors.update(form_errors)

        return self.errors

    @timed
    def _attribute_names(self) -> List[str]:
        """
        Gets publicly available attribute names. Cached in `_attribute_names_cache`.
        """
        non_callables = [
            member[0] for member in inspect.getmembers(self, lambda x: not callable(x))
        ]
        attribute_names = [name for name in non_callables if self._is_public(name)]

        return attribute_names

    @timed
    def _attributes(self) -> Dict[str, Any]:
        """
        Get publicly available attributes and their values from the component.
        """

        attribute_names = self._attribute_names_cache
        attributes = {}

        for attribute_name in attribute_names:
            attributes[attribute_name] = getattr(self, attribute_name)

        return attributes

    @timed
    def _set_property(self, name, value):
        # Get the correct value type by using the form if it is available
        data = self._attributes()
        data[name] = value
        form = self._get_form(data)

        if form and name in form.fields and name in form.cleaned_data:
            # The Django form CharField validator will remove whitespace
            # from the field value. Ignore that update if it's the
            # only thing different from the validator
            # https://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.CharField.strip
            if not hasattr(value, "strip") or form.cleaned_data[name] != value.strip():
                value = form.cleaned_data[name]

        updating_function_name = f"updating_{name}"
        if hasattr(self, updating_function_name):
            getattr(self, updating_function_name)(value)

        try:
            setattr(self, name, value)

            updated_function_name = f"updated_{name}"

            if hasattr(self, updated_function_name):
                getattr(self, updated_function_name)(value)
        except AttributeError as e:
            raise

    @timed
    def _methods(self) -> Dict[str, Callable]:
        """
        Get publicly available method names and their functions from the component.
        Cached in `_methods_cache`.
        """

        if self._methods_cache:
            return self._methods_cache

        member_methods = inspect.getmembers(self, inspect.ismethod)
        public_methods = [
            method for method in member_methods if self._is_public(method[0])
        ]
        methods = {k: v for (k, v) in public_methods}
        self._methods_cache = methods

        return methods

    @timed
    def _set_hook_methods_cache(self) -> None:
        """
        Caches the updating/updated attribute function names defined on the component.
        """
        self._hook_methods_cache = []

        for attribute_name in self._attribute_names_cache:
            updating_function_name = f"updating_{attribute_name}"
            updated_function_name = f"updated_{attribute_name}"
            hook_function_names = [updating_function_name, updated_function_name]

            for function_name in hook_function_names:
                if hasattr(self, function_name):
                    self._hook_methods_cache.append(function_name)

    @timed
    def _set_resettable_attributes_cache(self) -> None:
        """
        Caches the attributes that are "resettable" in `_resettable_attributes_cache`.
        Cache is a dictionary with key: attribute name; value: pickled attribute value

        Examples:
            - `UnicornField`
            - Django Models without a defined pk
        """
        self._resettable_attributes_cache = {}

        for attribute_name, attribute_value in self._attributes().items():
            if isinstance(attribute_value, UnicornField):
                self._resettable_attributes_cache[attribute_name] = pickle.dumps(
                    attribute_value
                )
            elif isinstance(attribute_value, Model):
                if not attribute_value.pk:
                    if attribute_name not in self._resettable_attributes_cache:
                        try:
                            self._resettable_attributes_cache[
                                attribute_name
                            ] = pickle.dumps(attribute_value)
                        except pickle.PickleError:
                            logger.warn(
                                f"Caching '{attribute_name}' failed because it could not be pickled."
                            )
                            pass

    def _is_public(self, name: str) -> bool:
        """
        Determines if the name should be sent in the context.
        """

        # Ignore some standard attributes from TemplateView
        protected_names = (
            "render",
            "request",
            "args",
            "kwargs",
            "content_type",
            "extra_context",
            "http_method_names",
            "template_engine",
            "template_name",
            "dispatch",
            "id",
            "get",
            "get_context_data",
            "get_template_names",
            "render_to_response",
            "http_method_not_allowed",
            "options",
            "setup",
            "fill",
            # Component methods
            "component_id",
            "component_name",
            "component_key",
            "reset",
            "mount",
            "hydrate",
            "updating",
            "update",
            "calling",
            "called",
            "complete",
            "rendered",
            "parent_rendered",
            "validate",
            "is_valid",
            "get_frontend_context_variables",
            "errors",
            "updated",
            "parent",
            "children",
            "call",
            "calls",
            "component_cache_key",
        )
        excludes = []

        if hasattr(self, "Meta") and hasattr(self.Meta, "exclude"):
            if isinstance(self.Meta.exclude, Sequence):
                excludes = self.Meta.exclude

        return not (
            name.startswith("_")
            or name in protected_names
            or name in self._hook_methods_cache
            or name in excludes
        )

    @staticmethod
    @timed
    def create(
        component_id: str,
        component_name: str,
        component_key: str = "",
        parent: "UnicornView" = None,
        request: HttpRequest = None,
        use_cache=True,
        kwargs: Dict[str, Any] = {},
    ) -> "UnicornView":
        """
        Find and instantiate a component class based on `component_name`.

        Args:
            param component_id: Id of the component. Required.
            param component_name: Name of the component. Used to locate the correct `UnicornView`
                component class and template if necessary. Required.
            param component_key: Key of the component to allow multiple components of the same name
                to be differentiated. Optional.
            param parent: The parent component of the current component.
            param kwargs: Keyword arguments for the component passed in from the template. Defaults to `{}`.
        
        Returns:
            Instantiated `UnicornView` component.
            Raises `ComponentLoadError` if the component could not be loaded.
        """
        assert component_id, "Component id is required"
        assert component_name, "Component name is required"

        @timed
        def _get_component_class(
            module_name: str, class_name: str
        ) -> Type[UnicornView]:
            """
            Imports a component based on module and class name.
            """
            module = importlib.import_module(module_name)
            component_class = getattr(module, class_name)

            return component_class

        cache = caches[get_cache_alias()]
        component_cache_key = f"unicorn:component:{component_id}"
        cached_component = cache.get(component_cache_key)

        if cached_component:
            # Get the newest version of the parent from cache if it is available
            # This needs to happen for Django cache because instances is pickled, so
            # a change in the view won't be reflected automatically (like with the module
            # cache) so it needs to be retrieved manually.
            if cached_component.parent:
                cached_parent_component = cache.get(
                    cached_component.parent.component_cache_key
                )

                if cached_parent_component:
                    cached_component.parent = cached_parent_component
                    cached_component.parent.setup(request)
        else:
            cached_component = constructed_views_cache.get(component_id)

        if use_cache and cached_component:
            # Note that `hydrate()` and `complete` don't need to be called here
            # because this path only happens for re-rendering from the view
            cached_component.setup(request)
            cached_component._validate_called = False
            cached_component.calls = []
            logger.debug(f"Retrieve {component_id} from constructed views cache")

            return cached_component

        if component_id in views_cache:
            (component_class, parent, kwargs) = views_cache[component_id]

            component = construct_component(
                component_class=component_class,
                component_id=component_id,
                component_name=component_name,
                component_key=component_key,
                parent=parent,
                request=request,
                **kwargs,
            )
            logger.debug(f"Retrieve {component_id} from views cache")

            return component

        locations = []

        if component_name in location_cache:
            locations.append(location_cache[component_name])
        else:
            locations = get_locations(component_name)

        # Store the last exception that got raised while looking for a component in case it is useful context
        last_exception: Union[
            Optional[ModuleNotFoundError], Optional[AttributeError]
        ] = None

        for (class_name, module_name) in locations:
            try:
                component_class = _get_component_class(module_name, class_name)
                component = construct_component(
                    component_class=component_class,
                    component_id=component_id,
                    component_name=component_name,
                    component_key=component_key,
                    parent=parent,
                    request=request,
                    **kwargs,
                )

                # Put the location for the component name in a module cache
                location_cache[component_name] = (class_name, module_name)

                # Put the component's class in a module cache
                views_cache[component_id] = (component_class, parent, kwargs)

                # Put the instantiated component into a module cache and the Django cache
                cacheable_component = None

                try:
                    cacheable_component = get_cacheable_component(component)
                except UnicornCacheError as e:
                    logger.warning(e)

                if cacheable_component:
                    if COMPONENTS_MODULE_CACHE_ENABLED:
                        constructed_views_cache[component_id] = cacheable_component

                    cache.set(
                        cacheable_component.component_cache_key, cacheable_component
                    )

                return component
            except ModuleNotFoundError as e:
                last_exception = e
            except AttributeError as e:
                last_exception = e

        raise ComponentLoadError(
            f"'{component_name}' component could not be loaded."
        ) from last_exception
