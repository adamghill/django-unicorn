import logging
import re
from collections import deque
from typing import Deque

import orjson
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution
from bs4.element import Tag
from bs4.formatter import HTMLFormatter
from django.template.backends.django import Template
from django.template.response import TemplateResponse

from django_unicorn.decorators import timed
from django_unicorn.errors import (
    MissingComponentElementError,
    MissingComponentViewElementError,
    MultipleRootComponentElementError,
    NoRootComponentElementError,
)
from django_unicorn.settings import get_minify_html_enabled, get_script_location
from django_unicorn.utils import generate_checksum, sanitize_html

logger = logging.getLogger(__name__)


# https://developer.mozilla.org/en-US/docs/Glossary/Empty_element
EMPTY_ELEMENTS = (
    "<area>",
    "<base>",
    "<br>",
    "<col>",
    "<embed>",
    "<hr>",
    "<img>",
    "<input>",
    "<link>",
    "<meta>",
    "<param>",
    "<source>",
    "<track>",
    "<wbr>",
)


def is_html_well_formed(html: str) -> bool:
    """
    Whether the passed-in HTML is missing any closing elements which can cause issues when rendering.
    """

    tag_list = re.split("(<[^>!]*>)", html)[1::2]
    stack: Deque[str] = deque()

    for tag in tag_list:
        if "/" not in tag:
            cleaned_tag = re.sub(r"(<([\w\-]+)[^>!]*>)", r"<\2>", tag)

            if cleaned_tag not in EMPTY_ELEMENTS:
                stack.append(cleaned_tag)
        elif len(stack) > 0 and (tag.replace("/", "") == stack[len(stack) - 1]):
            stack.pop()

    return len(stack) == 0


def assert_has_single_wrapper_element(root_element: Tag, component_name: str) -> None:
    """Assert that there is at least one child in the root element. And that there is only
    one root element.
    """

    # Check that the root element has at least one child
    try:
        next(root_element.descendants)
    except StopIteration:
        raise NoRootComponentElementError(
            f"The '{component_name}' component does not appear to have one root element."
        ) from None

    if "unicorn:view" in root_element.attrs or "u:view" in root_element.attrs:
        # If the root element is a direct view, skip the check
        return

    # Check that there is not more than one root element
    parent_element = root_element.parent

    tag_count = len([c for c in parent_element.children if isinstance(c, Tag)])

    if tag_count > 1:
        raise MultipleRootComponentElementError(
            f"The '{component_name}' component appears to have multiple root elements."
        ) from None


def _get_direct_view(tag: Tag):
    return tag.find_next(attrs={"unicorn:view": True}) or tag.find_next(attrs={"u:view": True})


def get_root_element(soup: BeautifulSoup) -> Tag:
    """Gets the first tag element for the component or the first element with a `unicorn:view` attribute for a direct
    view.

    Returns:
        BeautifulSoup tag element.

        Raises `Exception` if an element cannot be found.
    """

    for element in soup.contents:
        if isinstance(element, Tag) and element.name:
            if element.name == "html":
                view_element = _get_direct_view(element)

                if not view_element:
                    raise MissingComponentViewElementError(
                        "An element with an `unicorn:view` attribute is required for a direct view"
                    )

                return view_element

            return element

    raise MissingComponentElementError("No root element for the component was found")


class UnsortedAttributes(HTMLFormatter):
    """
    Prevent beautifulsoup from re-ordering attributes.
    """

    def __init__(self):
        super().__init__(entity_substitution=EntitySubstitution.substitute_html)

    def attributes(self, tag: Tag):
        yield from tag.attrs.items()


class UnicornTemplateResponse(TemplateResponse):
    def __init__(
        self,
        template,
        request,
        *,
        context=None,
        content_type=None,
        status=None,
        charset=None,
        using=None,
        component=None,
        init_js=False,
        **kwargs,  # noqa: ARG002
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

        self.component = component
        self.init_js = init_js

    def resolve_template(self, template):
        """Override the TemplateResponseMixin to resolve a list of Templates.

        Calls the super which accepts a template object, path-to-template, or list of paths if the first
        object in the sequence is not a Template.
        """

        if isinstance(template, (list, tuple)):
            if isinstance(template[0], Template):
                return template[0]

        return super().resolve_template(template)

    @timed
    def render(self):
        response = super().render()

        if not self.component or not self.component.component_id:
            return response

        content = response.content.decode("utf-8")

        if not is_html_well_formed(content):
            logger.warning(
                f"The HTML in '{self.component.component_name}' appears to be missing a closing tag. That can \
potentially cause errors in Unicorn."
            )

        frontend_context_variables = self.component.get_frontend_context_variables()
        frontend_context_variables_dict = orjson.loads(frontend_context_variables)
        checksum = generate_checksum(frontend_context_variables_dict)

        # Use `html.parser` and not `lxml` because in testing it was no faster even with `cchardet`
        # despite https://thehftguy.com/2020/07/28/making-beautifulsoup-parsing-10-times-faster/
        soup = BeautifulSoup(content, features="html.parser")
        root_element = get_root_element(soup)

        try:
            assert_has_single_wrapper_element(root_element, self.component.component_name)
        except (NoRootComponentElementError, MultipleRootComponentElementError) as ex:
            logger.warning(ex)

        root_element["unicorn:id"] = self.component.component_id
        root_element["unicorn:name"] = self.component.component_name
        root_element["unicorn:key"] = self.component.component_key
        root_element["unicorn:checksum"] = checksum
        root_element["unicorn:data"] = frontend_context_variables
        root_element["unicorn:calls"] = orjson.dumps(self.component.calls).decode("utf-8")

        # Generate the checksum based on the rendered content (without script tag)
        content_hash = generate_checksum(UnicornTemplateResponse._desoupify(soup))

        if self.init_js:
            init = {
                "id": self.component.component_id,
                "name": self.component.component_name,
                "key": self.component.component_key,
                "data": orjson.loads(frontend_context_variables),
                "calls": self.component.calls,
                "hash": content_hash,
            }
            init = orjson.dumps(init).decode("utf-8")
            json_element_id = f"unicorn:data:{self.component.component_id}"
            init_script = (
                f"Unicorn.componentInit(JSON.parse(document.getElementById('{json_element_id}').textContent));"
            )

            json_tag = soup.new_tag("script")
            json_tag["type"] = "application/json"
            json_tag["id"] = json_element_id
            json_tag.string = sanitize_html(init)

            if self.component.parent:
                self.component._init_script = init_script
                self.component._json_tag = json_tag
            else:
                json_tags = [json_tag]

                descendants = []
                descendants.append(self.component)
                while descendants:
                    descendant = descendants.pop()
                    for child in descendant.children:
                        init_script = f"{init_script} {child._init_script}"
                        json_tags.append(child._json_tag)
                        descendants.append(child)

                script_tag = soup.new_tag("script")
                script_tag["type"] = "module"
                script_tag.string = f"if (typeof Unicorn === 'undefined') {{ console.error('Unicorn is missing. Do you \
need {{% load unicorn %}} or {{% unicorn_scripts %}}?') }} else {{ {init_script} }}"

                if get_script_location() == "append":
                    root_element.append(script_tag)
                else:
                    root_element.insert_after(script_tag)

                for t in json_tags:
                    if get_script_location() == "append":
                        root_element.append(t)
                    else:
                        root_element.insert_after(t)

        rendered_template = UnicornTemplateResponse._desoupify(soup)
        self.component.rendered(rendered_template)

        response.content = rendered_template

        if get_minify_html_enabled():
            # Import here in case the minify extra was not installed
            from htmlmin import minify

            minified_html = minify(response.content.decode())

            if len(minified_html) < len(rendered_template):
                response.content = minified_html

        return response

    @staticmethod
    def _desoupify(soup):
        soup.smooth()
        return soup.encode(formatter=UnsortedAttributes()).decode("utf-8")
