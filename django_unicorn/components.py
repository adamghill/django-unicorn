import importlib
import inspect
import logging
import pickle
from typing import Any, Callable, Dict, List, Optional, Type, Union

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView

import orjson
import shortuuid
from bs4 import BeautifulSoup
from bs4.element import Tag
from bs4.formatter import HTMLFormatter

from . import serializer
from .settings import get_setting
from .utils import generate_checksum


logger = logging.getLogger(__name__)


# Module cache to reduce initialization costs
views_cache = {}
constructed_views_cache = {}


class UnicornField:
    """
    Can be used to provide a way to serialize a class quickly.
    Probably not a good idea in lots of cases.
    """

    def to_json(self):
        return self.__dict__


class ComponentLoadError(Exception):
    pass


class UnsortedAttributes(HTMLFormatter):
    """
    Prevent beautifulsoup from re-ordering attributes.
    """

    def attributes(self, tag: Tag):
        for k, v in tag.attrs.items():
            yield k, v


def convert_to_snake_case(s: str) -> str:
    # TODO: Better handling of dash->snake
    return s.replace("-", "_")


def convert_to_camel_case(s: str) -> str:
    # TODO: Better handling of dash/snake->camel-case
    s = convert_to_snake_case(s)
    return "".join(word.title() for word in s.split("_"))


class UnicornTemplateResponse(TemplateResponse):
    def __init__(
        self,
        template,
        request,
        context=None,
        content_type=None,
        status=None,
        charset=None,
        using=None,
        component_name=None,
        component_id=None,
        frontend_context_variables={},
        init_js=False,
        **kwargs,
    ):
        super().__init__(
            template=template,
            request=request,
            context=context,
            content_type=content_type,
            status=status,
            charset=charset,
            using=using,
        )

        self.component_id = component_id
        self.component_name = component_name
        self.frontend_context_variables = frontend_context_variables
        self.init_js = init_js

    def render(self):
        response = super().render()

        if not self.component_id:
            return response

        content = response.content.decode("utf-8")

        checksum = generate_checksum(str.encode(str(self.frontend_context_variables)))

        soup = BeautifulSoup(content, features="html.parser")
        root_element = UnicornTemplateResponse._get_root_element(soup)
        root_element["unicorn:id"] = self.component_id
        root_element["unicorn:name"] = self.component_name
        root_element["unicorn:checksum"] = checksum

        if self.init_js:
            script_tag = soup.new_tag("script")
            init = {
                "id": self.component_id,
                "name": self.component_name,
                "data": orjson.loads(self.frontend_context_variables),
            }
            init = orjson.dumps(init).decode("utf-8")
            script_tag["type"] = "module"
            script_tag.string = f"if (typeof Unicorn === 'undefined') {{ console.error('Unicorn is missing. Do you need {{% load unicorn %}} or {{% unicorn-scripts %}}?') }} else {{ Unicorn.componentInit({init}); }}"
            root_element.insert_after(script_tag)

        rendered_template = UnicornTemplateResponse._desoupify(soup)
        rendered_template = mark_safe(rendered_template)

        response.content = rendered_template
        return response

    @staticmethod
    def _get_root_element(soup: BeautifulSoup) -> Tag:
        """
        Gets the first div element.

        Returns:
            BeautifulSoup element.
            
            Raises an Exception if a div cannot be found.
        """
        for element in soup.contents:
            if element.name and element.name == "div":
                return element

        raise Exception("No root element found")

    @staticmethod
    def _desoupify(soup):
        soup.smooth()
        return soup.encode(formatter=UnsortedAttributes()).decode("utf-8")


class UnicornView(TemplateView):
    response_class = UnicornTemplateResponse
    component_name: str = ""
    request = None

    # Caches to reduce the amount of time introspecting the class
    _methods_cache: Dict[str, Callable] = {}
    _attribute_names_cache: List[str] = []
    _hook_methods_cache: List[str] = []

    # Dictionary with key: attribute name; value: pickled attribute value
    _resettable_attributes_cache: Dict[str, Any] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        assert self.component_name, "Component name is required"

        if "component_id" not in kwargs or not kwargs["component_id"]:
            self.component_id = shortuuid.uuid()[:8]

        if "request" in kwargs:
            self.setup(kwargs["request"])

        self._validate_called = False
        self.errors = {}
        self._set_default_template_name()
        self._set_caches()

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
            self.template_name = f"unicorn/{self.component_name}.html"

    def _set_caches(self) -> None:
        """
        Setup some initial "caches" to prevent Python from having to introspect
        a component UnicornView for methods and properties multiple times.
        """
        self._attribute_names_cache = self._attribute_names()
        self._set_hook_methods_cache()
        self._methods_cache = self._methods()
        self._set_resettable_attributes_cache()

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

    def mount(self):
        """
        Hook that gets called when a component is first created.
        """
        pass

    def hydrate(self):
        """
        Hook that gets called when a component's data is hydrated.
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

    def render(self, init_js=False) -> str:
        """
        Renders a UnicornView component with the public properties available. Delegates to a
        UnicornTemplateResponse to actually render a response.
 
        Args:
            param init_js: Whether or not to include the Javascript required to initialize the component.
        """
        frontend_context_variables = self.get_frontend_context_variables()

        response = self.render_to_response(
            context=self.get_context_data(),
            component_name=self.component_name,
            component_id=self.component_id,
            frontend_context_variables=frontend_context_variables,
            init_js=init_js,
        )

        # render_to_response() could only return a HttpResponse, so check for render()
        if hasattr(response, "render"):
            response.render()

        rendered_component = response.content.decode("utf-8")

        return rendered_component

    def get_frontend_context_variables(self) -> str:
        """
        Get publicly available properties and output them in a string-encoded JSON object.
        """

        frontend_context_variables = {}
        attributes = self._attributes()
        frontend_context_variables.update(attributes)

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
                        frontend_context_variables[key] = value

        encoded_frontend_context_variables = serializer.dumps(
            frontend_context_variables
        )

        return encoded_frontend_context_variables

    def _get_form(self, data):
        if hasattr(self, "form_class"):
            try:
                form = self.form_class(data)
                form.is_valid()

                return form
            except Exception as e:
                logger.exception(e)

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

    def is_valid(self, model_names: List = None) -> bool:
        return len(self.validate(model_names).keys()) == 0

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

    def _attribute_names(self) -> List[str]:
        """
        Gets publicly available attribute names. Cached in `_attribute_names_cache`.
        """
        non_callables = [
            member[0] for member in inspect.getmembers(self, lambda x: not callable(x))
        ]
        attribute_names = [name for name in non_callables if self._is_public(name)]

        return attribute_names

    def _attributes(self) -> Dict[str, Any]:
        """
        Get publicly available attributes and their values from the component.
        """

        attribute_names = self._attribute_names_cache
        attributes = {}

        for attribute_name in attribute_names:
            attributes[attribute_name] = getattr(self, attribute_name)

        return attributes

    def _set_property(self, name, value):
        # Get the correct value type by using the form if it is available
        data = self._attributes()
        data[name] = value
        form = self._get_form(data)

        if form and name in form.fields and name in form.cleaned_data:
            value = form.cleaned_data[name]

        updating_function_name = f"updating_{name}"
        if hasattr(self, updating_function_name):
            getattr(self, updating_function_name)(value)

        try:
            setattr(self, name, value)

            updated_function_name = f"updated_{name}"

            if hasattr(self, updated_function_name):
                getattr(self, updated_function_name)(value)
        except AttributeError:
            logger.error(
                f"'{name}' attribute on '{self.component_name}' component could not be set. Is it a @property without a setter?"
            )

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
            "reset",
            "mount",
            "hydrate",
            "updating",
            "update",
            "calling",
            "called",
            "validate",
            "is_valid",
            "get_frontend_context_variables",
            "errors",
            "updated",
        )
        excludes = []

        if hasattr(self, "Meta") and hasattr(self.Meta, "exclude"):
            excludes = self.Meta.exclude

        return not (
            name.startswith("_")
            or name in protected_names
            or name in self._hook_methods_cache
            or name in excludes
        )

    @staticmethod
    def create(
        component_name: str, component_id: str = None, use_cache=True
    ) -> "UnicornView":
        """
        Find and instantiate a component class based on `component_name`.

        Args:
            param component_name: Name of the component. Used to locate the correct `UnicornView`
                component class and template if necessary.
            param component_id: Id of the component. Will be created if not passed in.
            param use_cache: Get component from cache or force construction of component. Defaults to `True`.
        
        Returns:
            Instantiated `UnicornView` component.
            Raises `ComponentLoadError` if the component could not be loaded.
        """
        if component_id and use_cache:
            key = f"{component_name}-{component_id}"

            if key in constructed_views_cache:
                component = constructed_views_cache[key]
                component._validate_called = False
                return component

        if component_name in views_cache:
            component = views_cache[component_name](
                component_name=component_name, component_id=component_id
            )

            #  Re-initializes classes so that `reset` magic method will "clear" them as expected
            component.reset()

            component.hydrate()

            if component_id:
                key = f"{component_name}-{component_id}"
                constructed_views_cache[key] = component

            component._validate_called = False

            return component

        locations = []

        def _get_component_class(
            module_name: str, class_name: str
        ) -> Type[UnicornView]:
            """
            Imports a component based on module and class name.
            """
            module = importlib.import_module(module_name)
            component_class = getattr(module, class_name)

            return component_class

        if "." in component_name:
            # Handle fully-qualified component names (e.g. `project.unicorn.HelloWorldView`)
            class_name = component_name.split(".")[-1:][0]
            module_name = component_name.replace("." + class_name, "")
            locations.append((class_name, module_name))
        else:
            # Use conventions to find the component class
            class_name = convert_to_camel_case(component_name)
            class_name = f"{class_name}View"
            module_name = convert_to_snake_case(component_name)

            unicorn_apps = get_setting("APPS", ["unicorn"])

            assert (
                isinstance(unicorn_apps, list)
                or isinstance(unicorn_apps, tuple)
                or isinstance(unicorn_apps, set)
            ), "APPS is expected to be a list, tuple or set"

            for app in unicorn_apps:
                app_module_name = f"{app}.components.{module_name}"
                locations.append((class_name, app_module_name))

        # TODO: django.conf setting bool that defines whether to look in all installed apps for components

        # Store the last exception that got raised while looking for a component in case it is useful context
        last_exception: Union[
            Optional[ModuleNotFoundError], Optional[AttributeError]
        ] = None

        for (class_name, module_name) in locations:
            try:
                component_class = _get_component_class(module_name, class_name)
                component = component_class(
                    component_name=component_name, id=component_id
                )
                component.mount()
                component.hydrate()

                views_cache[component_name] = component_class

                return component
            except ModuleNotFoundError as e:
                last_exception = e
            except AttributeError as e:
                last_exception = e

        raise ComponentLoadError(
            f"'{component_name}' component could not be loaded."
        ) from last_exception
