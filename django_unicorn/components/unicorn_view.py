import importlib
import logging
import pickle
from functools import cache
import re
from inspect import getmembers, isclass

import orjson
import shortuuid
from django.apps import apps as django_apps_module
from django.db.models import Model
from django.forms.widgets import CheckboxInput, Select
from django.http import HttpRequest
from django.utils.decorators import classonlymethod
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView

from django_unicorn import serializer
from django_unicorn.cacher import cache_full_tree, restore_from_cache
from django_unicorn.components.fields import UnicornField
from django_unicorn.components.unicorn_template_response import UnicornTemplateResponse
from django_unicorn.decorators import timed
from django_unicorn.typer import cast_attribute_value, get_type_hints
from django_unicorn.utils import is_non_string_sequence

try:
    from cachetools.lru import LRUCache
except ImportError:
    from cachetools import LRUCache


logger = logging.getLogger(__name__)

LOCAL_COMPONENT_CACHE = LRUCache(maxsize=1_000)


class Component(TemplateView):

    component_key: str = ""
    component_id: str = ""
    component_args: list = None
    component_kwargs: dict = None
    
    response_class = UnicornTemplateResponse
    
    request: HttpRequest = None
    
    parent: "Component" = None
    
    children: list["Component"] = None
    
    force_render: bool = False
    
    # JavaScript method calls
    calls: list = None
    
    errors: dict = None
    
    _validate_called: bool = False
    _init_script: str = ""
    
    component_args: list = None
    component_kwargs: dict = None

    def __init__(
            self, 
            component_args: list = [], 
            component_kwargs: dict = {}, 
            **kwargs,
        ):
        
        # super().__init__(**kwargs) --> same as below
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        if kwargs.get("id"):
            # Sometimes the component_id is initially in kwargs["id"]
            self.component_id = kwargs["id"]

        if not self.component_id:
            raise AssertionError("Component id is required")

        # init mutable sets with a fresh start
        self.children = []
        self.calls = []
        self.errors = {}

        # set parent-child relationships
        if self.parent and self not in self.parent.children:
            self.parent.children.append(self)
        
        # !!! not sure when/where this is used
        self.component_args = component_args
        
        # Revise the kwargs to only include custom kwargs since the 
        # standard kwargs are available as instance variables
        custom_kwargs = set(component_kwargs.keys()) - {
            # STANDARD_COMPONENT_KWARG_KEYS
            "id",
            "component_id",
            "component_name",
            "component_key",
            "parent",
            "request",
        }
        self.component_kwargs = {k: component_kwargs[k] for k in list(custom_kwargs)}
        
        # apply kwargs
        for key, value in self.component_kwargs.items():
            setattr(self, key, value)
        
        # !!! should kwargs be mounted only on __init__ or should this move
        # to the get_or_create method?
        self.mount()
        
        # Make sure that there is always a request on the parent if needed
        # if self.parent is not None and self.parent.request is None:
        #     self.parent.request = self.request

        # component.hydrate()
        # component.complete()
        # component._validate_called = False

        self.to_local_cache()
        # component._set_request(request)

    @classmethod
    @property
    def component_name(cls):
        # Switch from class name to unicorn convent (ExampleNameView --> example-name)
        # adds a hyphen between each capital letter
        # copied from https://stackoverflow.com/questions/199059/
        # -4 is to remove "View" at end
        return re.sub(r"(\w)([A-Z])", r"\1-\2", cls.__name__[:-4]).lower()

    @classmethod
    @property
    def template_name(self) -> str:
        """
        Sets a default template name based on component's name if necessary.
        """
        # Convert component name with a dot to a folder structure
        template_name = self.component_name.replace(".", "/")
        self.template_name = f"unicorn/{template_name}.html"

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
    
    # -------------------------------------------------------------------------
    
    def reset(self):
        for (
            attribute_name,
            pickled_value,
        ) in self._resettable_attributes.items():
            try:
                attribute_value = pickle.loads(pickled_value)  # noqa: S301
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

    @classonlymethod
    def as_view(cls, **initkwargs):  # noqa: N805
        if "component_id" not in initkwargs:
            initkwargs["component_id"] = shortuuid.uuid()[:8]

        if "component_name" not in initkwargs:
            module_name = cls.__module__
            module_parts = module_name.split(".")
            component_name = module_parts[-1].replace("_", "-")

            initkwargs["component_name"] = component_name

        return super().as_view(**initkwargs)

    @timed
    def render(self, *, init_js=False, extra_context=None, request=None) -> str:
        """
        Renders a UnicornView component with the public properties available. Delegates to a
        UnicornTemplateResponse to actually render a response.

        Args:
            param init_js: Whether or not to include the Javascript required to initialize the component.
            param extra_context:
            param request: Set the `request` for rendering. Usually it will be in the context,
                but it is missing when the component is re-rendered as a direct view, so it needs
                to be set explicitly.
        """

        if extra_context is not None:
            self.extra_context = extra_context

        if request:
            self.request = request

        response = self.render_to_response(
            context=self.get_context_data(),
            component=self,
            init_js=init_js,
        )

        # render_to_response() could only return a HttpResponse, so check for render()
        if hasattr(response, "render"):
            response.render()

        rendered_component = response.content.decode("utf-8")

        return rendered_component

    def dispatch(self, request, *args, **kwargs):  # noqa: ARG002
        """
        Called by the `as_view` class method when utilizing a component directly as a view.
        """

        self.mount()
        self.hydrate()

        return self.render_to_response(
            context=self.get_context_data(),
            component=self,
            init_js=True,
        )

    # Ideally, this would be named get_frontend_context_json
    def get_frontend_context_variables(self) -> str:
        """
        Get publicly available properties and output them in a string-encoded JSON object.
        """
        frontend_context_variables = {}
        attributes = self._attributes
        frontend_context_variables.update(attributes)

        exclude_field_attributes = []

        # Remove any field in `javascript_exclude` from `frontend_context_variables`
        if hasattr(self, "Meta") and hasattr(self.Meta, "javascript_exclude"):
            if type(self.Meta.javascript_exclude) in (list, tuple):
                for field_name in self.Meta.javascript_exclude:
                    if "." in field_name:
                        # Because the dictionary value could be an object, we can't just remove the attribute, so
                        # store field attributes for later to remove them from the serialized dictionary
                        exclude_field_attributes.append(field_name)
                    else:
                        if field_name not in frontend_context_variables:
                            raise serializer.InvalidFieldNameError(
                                field_name=field_name, data=frontend_context_variables
                            )

                        del frontend_context_variables[field_name]

        # Add cleaned values to `frontend_content_variables` based on the widget in form's fields
        form = self._get_form(attributes)

        if form:
            for key in attributes.keys():
                if key in form.fields:
                    field = form.fields[key]

                    if key in form.cleaned_data:
                        cleaned_value = form.cleaned_data[key]

                        if isinstance(field.widget, CheckboxInput) and isinstance(
                            cleaned_value, bool
                        ):
                            # Handle booleans for checkboxes explicitly because `format_value`
                            # returns `None`
                            value = cleaned_value
                        elif (
                            isinstance(field.widget, Select)
                            and not field.widget.allow_multiple_selected
                        ):
                            # Handle value for Select widgets explicitly because `format_value`
                            # returns a list of stringified values
                            value = cleaned_value
                        else:
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
            frontend_context_variables,
            exclude_field_attributes=tuple(exclude_field_attributes),
        )

        return encoded_frontend_context_variables

    @timed
    def get_frontend_context(self) -> str:
        """
        Get publicly available properties and output them to a python dict.
        Note, special types (e.g. db models) are converted to dict as well
        """
        # Re-load frontend context variables to deal with non-serializable properties.
        # OPTMIZE: this converts to json and then immediately back to dict...
        # !!! method easily confused with `get_frontend_context`, which is for template
        return orjson.loads(self.get_frontend_context_variables())

    @timed
    def _get_form(self, data):
        if hasattr(self, "form_class"):
            try:
                form = self.form_class(data=data)
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

        attributes = self._attributes
        context.update(attributes)
        context.update(self._methods)
        context.update(
            {
                "unicorn": {
                    "component_id": self.component_id,
                    "component_name": self.component_name,
                    "component_key": self.component_key,
                    "component": self,
                    "errors": self.errors,
                }
            }
        )

        return context


    def is_valid(self, model_names: list = None) -> bool:
        return len(self.validate(model_names).keys()) == 0

    def validate(self, model_names: list = None) -> dict:
        """
        Validates the data using the `form_class` set on the component.

        Args:
            model_names: Only include validation errors for specified fields. If none, validate everything.
        """
        # TODO: Handle form.non_field_errors()?

        if self._validate_called:
            return self.errors

        self._validate_called = True

        data = self._attributes
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
    
    # -------------------------------------------------------------------------

    @classmethod
    @property
    @cache
    def _methods(cls) -> dict[str, callable]:
        """
        Get publicly available method names and their functions from the component.
        Cached in `_methods_cache`.
        """
        return {
            name: getattr(cls, name)
            for name in dir(cls)
            # name="_methods" will cause recursion error
            if cls._is_public(name) and callable(getattr(cls, name)) 
        }  # dir() looks to be faster than inspect.getmembers

    @classmethod
    @property
    @cache
    def _hook_methods(cls) -> list:
        """
        Caches the updating/updated attribute function names defined on the component.
        """
        hook_methods = []
        # BUG: using 'cls._attribute_names' causes recursion due to is_public method
        for attribute_name in dir(cls): 
            for hook_name in ["updating", "updated"]:
                function_name = f"{hook_name}_{attribute_name}"
                if hasattr(cls, function_name):
                    hook_methods.append(function_name)
        return hook_methods

    @classmethod
    @property
    @cache
    def _attribute_names(cls) -> list[str]:
        """
        Gets publicly available attribute names.
        """
        attribute_names = [
            name
            for name in dir(cls)
            # name="_methods" will cause recursion error
            if cls._is_public(name) and not callable(getattr(cls, name)) 
        ]  # dir() looks to be faster than inspect.getmembers

        # Add type hints for the component to the attribute names since
        # they won't be returned from `getmembers`/`dir`
        for type_hint_attribute_name in get_type_hints(cls).keys():
            if cls._is_public(type_hint_attribute_name):
                if type_hint_attribute_name not in attribute_names:
                    attribute_names.append(type_hint_attribute_name)

        return attribute_names

    @property
    def _attributes(self) -> dict[str, any]:
        """
        Get publicly available attributes and their values from the component.
        """
        return {attribute_name: getattr(self, attribute_name, None) for attribute_name in self._attribute_names}
    
    @property
    def _resettable_attributes(self) -> dict:
        """
        attributes that are "resettable"
        a dictionary with key: attribute name; value: pickled attribute value

        Examples:
            - `UnicornField`
            - Django Models without a defined pk
        """
        resettable_attributes = {}
        for attribute_name, attribute_value in self._attributes.items():
            if isinstance(attribute_value, UnicornField):
                resettable_attributes[attribute_name] = pickle.dumps(
                    attribute_value
                )
            elif isinstance(attribute_value, Model):
                if not attribute_value.pk:
                    if attribute_name not in resettable_attributes:
                        try:
                            resettable_attributes[
                                attribute_name
                            ] = pickle.dumps(attribute_value)
                        except pickle.PickleError:
                            logger.warn(
                                f"Caching '{attribute_name}' failed because it could not be pickled."
                            )
                            pass
        return resettable_attributes
    
    # -------------------------------------------------------------------------
    
    @timed
    def _set_property(
        self,
        name: str,
        value: any,
        *,
        call_updating_method: bool = False,
        call_updated_method: bool = False,
    ) -> None:
        # Get the correct value type by using the form if it is available
        data = self._attributes

        value = cast_attribute_value(self, name, value)
        data[name] = value

        form = self._get_form(data)

        if form and name in form.fields and name in form.cleaned_data:
            # The Django form CharField validator will remove whitespace
            # from the field value. Ignore that update if it's the
            # only thing different from the validator
            # https://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.CharField.strip
            if not hasattr(value, "strip") or form.cleaned_data[name] != value.strip():
                value = form.cleaned_data[name]

        if call_updating_method:
            updating_function_name = f"updating_{name}"

            if hasattr(self, updating_function_name):
                getattr(self, updating_function_name)(value)

        try:
            setattr(self, name, value)

            if call_updated_method:
                updated_function_name = f"updated_{name}"

                if hasattr(self, updated_function_name):
                    getattr(self, updated_function_name)(value)
        except AttributeError:
            raise

    @timed
    def _get_property(self, property_name: str) -> any:
        """
        Gets property value from the component based on the property name.
        Handles nested property names.

        Args:
            param component: Component to get property values from.
            param property_name: Property name. Can be "dot-notation" to get nested properties.
        """

        if property_name is None:
            raise AssertionError("property_name name is required")

        # Handles nested properties
        property_name_parts = property_name.split(".")
        component_or_field = self

        for idx, property_name_part in enumerate(property_name_parts):
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
    
    # -------------------------------------------------------------------------
    
    @classmethod
    def _is_public(cls, name: str) -> bool:
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
            "view_is_async",
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
            "component_kwargs",
            "component_args",
            "force_render",
        )

        excludes = []
        if hasattr(cls, "Meta") and hasattr(cls.Meta, "exclude"):
            if not is_non_string_sequence(cls.Meta.exclude):
                raise AssertionError("Meta.exclude should be a list, tuple, or set")

            for exclude in cls.Meta.exclude:
                if not hasattr(cls, exclude):
                    raise serializer.InvalidFieldNameError(
                        field_name=exclude, data=cls._attributes()
                    )

            excludes = cls.Meta.exclude

        return not (
            name.startswith("_")
            or name in protected_names
            or name in cls._hook_methods
            or name in excludes
        )
    
    def _mark_safe_fields(self):
        # Get set of attributes that should be marked as `safe`
        safe_fields = []
        if hasattr(self, "Meta") and hasattr(self.Meta, "safe"):
            breakpoint()
            if isinstance(self.Meta.safe, Sequence):
                for field_name in self.Meta.safe:
                    if field_name in self._attributes.keys():
                        safe_fields.append(field_name)

        # Mark safe attributes as such before rendering
        for field_name in safe_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, mark_safe(value))
    
    # -------------------------------------------------------------------------

    @classmethod
    def from_request(
            cls,
            request, # takes ComponentRequest, not HttpRequest
            apply_actions: bool = True,
        ):
        """
        Given a ComponentRequest object, this will create or load from cache
        the proper UnicornView object and then (if requested) apply all actions 
        to the UnicornView object.
        """
        component = cls.get_or_create(
            component_id=request.id,
            component_name=request.name,
            request=request.request,  # gives the HttpRequest obj
        )

        if apply_actions:
            request.apply_to_component(component, inplace=True)

        return component

    @classmethod
    def get_or_create(
        cls,
        component_id: str,
        component_name: str,
        **kwargs,
    ) -> "UnicornView":

        component_cache_key = f"unicorn:component:{component_id}"

        # try local cache
        cached_component = cls.from_local_cache(component_cache_key)
        if cached_component:
            print(f"get {component_id}")
            return cached_component
        
        # try django cache  (DISABLED FOR NOW)
        # cached_component = cls.from_django_cache(component_cache_key)
        # if cached_component:
        #     return cached_component
        
        # create new one
        print(f"create {component_id}")
        return cls.create(
            component_id=component_id,
            component_name=component_name,
            **kwargs,
        )
    
    @staticmethod
    def from_local_cache(component_cache_key: str) -> "UnicornView":
        return LOCAL_COMPONENT_CACHE.get(component_cache_key)
    
    @staticmethod
    def from_django_cache(component_cache_key: str) -> "UnicornView":
        return restore_from_cache(component_cache_key)
    
    @staticmethod
    def create(component_name: str, **kwargs) -> "UnicornView":
        # note this fxn call is cached for speedup
        component_class = get_all_component_classes()[component_name]
        return component_class(**kwargs)
    
    # -------------------------------------------------------------------------
    
    @property
    def component_cache_key(self):
        return f"unicorn:component:{self.component_id}"
        # return (
        #     f"{self.parent._component_cache_key}:{self.component_id}" 
        #     if self.parent 
        #     else f"unicorn:component:{self.component_id}"
        # )

    def update_caches(self):
        self.to_local_cache()
        # self.to_django_cache()  # DISABLE FOR NOW
    
    def to_local_cache(self):
        LOCAL_COMPONENT_CACHE[self.component_cache_key] = self
    
    def to_django_cache(self):
        cache_full_tree(self)

    # -------------------------------------------------------------------------


# modified from simmate get_all_workflows
@cache
def get_all_component_classes() -> dict:

    # note - app_config.name gives the python path
    apps_to_search = [app_config.name for app_config in django_apps_module.get_app_configs()]
    
    all_components = {}
    for app_name in apps_to_search:
        
        # check if there is a components module for this app and load it if so
        components_path = get_app_submodule(app_name, "components")
        if not components_path:
            continue  # skip to the next app
        app_components_module = importlib.import_module(components_path)

        # iterate through each available object in the components file and find
        # which ones are Component objects. This will be the file "components.py"
        # or "components/__init__.py"
        
        # SETUP OPTION 1
        # If an __all__ value is set, then this will take priority when grabbing
        # workflows from the module
        if hasattr(app_components_module, "__all__"):
            for component_class_name in app_components_module.__all__:
                if not component_class_name.endswith("View"):
                    continue  # !!! unicorn convention, I'd rather isinstance()  
                component_class = getattr(app_components_module, component_class_name)
                if component_class_name not in all_components:
                    all_components[component_class_name] = component_class
        
        # SETUP OPTION 2
        # otherwise we load ALL class objects from the module -- assuming the
        # user properly limited these to just Component objects.
        else:
            # a tuple is returned by getmembers so c[0] is the string name while
            # c[1] is the python class object.
            for component_class_name, component_class in getmembers(app_components_module):
                if not isclass(component_class):
                    continue
                if not component_class_name.endswith("View"):
                    continue  # !!! unicorn convention, I'd rather isinstance()
                if component_class_name not in all_components:
                    all_components[component_class_name] = component_class
    
    # Switch from class name to unicorn convent (ExampleNameView --> example-name)
    # adds a hyphen between each capital letter
    # copied from https://stackoverflow.com/questions/199059/
    # -4 is to remove "View" at end
    all_components_cleaned = {}
    for component_class_name, component_class in all_components.items():
        component_name = re.sub(r"(\w)([A-Z])", r"\1-\2", component_class_name[:-4]).lower()
        all_components_cleaned[component_name] = component_class

    return all_components_cleaned

# util borrowed from simmate
def get_app_submodule(
    app_path: str,
    submodule_name: str,
) -> str:
    """
    Checks if an app has a submodule present and returns the import path for it.
    This is useful for checking if there are workflows or urls defined, which
    are optional accross all apps. None is return if no app exists
    """
    submodule_path = f"{app_path}.{submodule_name}"

    # check if there is a workflows module in the app, and if so,
    # try loading the workflows.
    #   stackoverflow.com/questions/14050281
    has_submodule = importlib.util.find_spec(submodule_path) is not None

    return submodule_path if has_submodule else None

# util borrowed from simmate
def get_class(class_path: str):
    """
    Given the import path for a python class (e.g. path.to.MyClass), this
    utility will load the class given (MyClass).
    """
    config_modulename = ".".join(class_path.split(".")[:-1])
    config_name = class_path.split(".")[-1]
    config_module = importlib.import_module(config_modulename)
    config = getattr(config_module, config_name)
    return config


# to support deprec naming of class
UnicornView = Component
