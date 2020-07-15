import hmac
import importlib
import inspect
import uuid

from django.conf import settings
from django.template import Context
from django.template.engine import Engine
from django.utils.safestring import mark_safe

import orjson
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter


def convert_to_snake_case(s):
    # TODO: Better handling of dash->snake
    return s.replace("-", "_")


def convert_to_camel_case(s):
    # TODO: Better handling of dash/snake->camel-case
    s = convert_to_snake_case(s)
    return "".join(word.title() for word in s.split("_"))


class Component:
    def __init__(self, component_name, id=None):
        if not id:
            id = uuid.uuid4()

        self.id = id
        self.component_name = component_name

    @staticmethod
    def create(component_name, id=None):
        # TODO: Handle the module not being found
        module_name = convert_to_snake_case(component_name)
        module = importlib.import_module(f"unicorn.components.{module_name}")

        # TODO: Handle the class not being found
        class_name = convert_to_camel_case(module_name)
        component_class = getattr(module, class_name)

        return component_class(component_name, id=id)

    def __attributes__(self):
        """
        Get attributes that can be called in the component.
        """
        non_callables = [
            member[0] for member in inspect.getmembers(self, lambda x: not callable(x))
        ]
        attribute_names = list(
            filter(lambda name: self._is_public_name(name), non_callables,)
        )

        attributes = {}

        for attribute_name in attribute_names:
            attributes[attribute_name] = object.__getattribute__(self, attribute_name)

        return attributes

    def __methods__(self):
        """
        Get methods that can be called in the component.
        """

        # TODO: Should only take methods that only have self argument?
        member_methods = inspect.getmembers(self, inspect.ismethod)
        public_methods = filter(
            lambda method: self._is_public_name(method[0]), member_methods
        )
        methods = {k: v for (k, v) in public_methods}

        return methods

    def __context__(self):
        """
        Collects every thing that could be used in the template context.
        """
        return {
            "attributes": self.__attributes__(),
            "methods": self.__methods__(),
        }

    def render(self, template_context={}, include_component_init=True):
        context = self.__context__()
        context_variables = {}
        context_variables.update(context["attributes"])
        context_variables.update(context["methods"])
        context_variables.update(template_context)

        frontend_context_variables = {}
        frontend_context_variables.update(context["attributes"])
        frontend_context_variables = orjson.dumps(frontend_context_variables).decode(
            "utf-8"
        )

        checksum = hmac.new(
            str.encode(settings.SECRET_KEY),
            str.encode(frontend_context_variables),
            digestmod="sha256",
        ).hexdigest()

        if settings.DEBUG:
            context_variables.update({"unicorn_debug": context})

        template_engine = Engine.get_default()
        # TODO: Handle looking in other directories for templates
        template = template_engine.get_template(f"unicorn/{self.component_name}.html")
        context = Context(context_variables, autoescape=True)
        rendered_template = template.render(context)

        soup = BeautifulSoup(rendered_template, features="html.parser")
        root_element = Component._get_root_element(soup)
        root_element["unicorn:id"] = str(self.id)
        root_element["unicorn:checksum"] = checksum

        if include_component_init:
            script = soup.new_tag("script")
            init = {
                "id": str(self.id),
                "name": self.component_name,
            }
            init = orjson.dumps(init).decode("utf-8")
            script.string = f"Unicorn.setData({frontend_context_variables}); Unicorn.componentInit({init});"
            root_element.insert_after(script)

        rendered_template = Component._desoupify(soup)
        rendered_template = mark_safe(rendered_template)

        return rendered_template

    def _is_public_name(self, name):
        """
        Determines if the name should be sent in the context.
        """
        protected_names = (
            "id",
            "render",
            "view",
        )
        excludes = []

        if hasattr(self, "Meta") and hasattr(self.Meta, "exclude"):
            excludes = self.Meta.exclude

        return not (name.startswith("_") or name in protected_names or name in excludes)

    @staticmethod
    def _get_root_element(soup):
        for element in soup.contents:
            if element.name and element.name == "div":
                return element

        raise Exception("No root element found")

    @staticmethod
    def _desoupify(soup):
        soup.smooth()
        return soup.encode(formatter=UnsortedAttributes()).decode("utf-8")


class UnsortedAttributes(HTMLFormatter):
    """
    Prevent beautifulsoup from re-ordering attributes.
    """

    def attributes(self, tag):
        for k, v in tag.attrs.items():
            yield k, v
