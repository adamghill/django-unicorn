import logging
import re
from collections import deque

from django.template.response import TemplateResponse

import orjson
from bs4 import BeautifulSoup
from bs4.dammit import EntitySubstitution
from bs4.element import Tag
from bs4.formatter import HTMLFormatter

from django_unicorn.settings import get_minify_html_enabled, get_script_location
from django_unicorn.utils import sanitize_html

from ..decorators import timed
from ..errors import MissingComponentElement, MissingComponentViewElement
from ..utils import generate_checksum


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
    stack = deque()

    for tag in tag_list:
        if "/" not in tag:
            cleaned_tag = re.sub(r"(<(\w+)[^>!]*>)", r"<\2>", tag)

            if cleaned_tag not in EMPTY_ELEMENTS:
                stack.append(cleaned_tag)
        elif len(stack) > 0 and (tag.replace("/", "") == stack[len(stack) - 1]):
            stack.pop()

    return len(stack) == 0


class UnsortedAttributes(HTMLFormatter):
    """
    Prevent beautifulsoup from re-ordering attributes.
    """

    def __init__(self):
        super().__init__(entity_substitution=EntitySubstitution.substitute_html)

    def attributes(self, tag: Tag):
        for k, v in tag.attrs.items():
            yield k, v


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
        component=None,
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

        self.component = component
        self.init_js = init_js

    @timed
    def render(self):
        response = super().render()

        if not self.component or not self.component.component_id:
            return response

        content = response.content.decode("utf-8")

        if not is_html_well_formed(content):
            logger.warning(
                f"The HTML in '{self.component.component_name}' appears to be missing a closing tag. That can potentially cause errors in Unicorn."
            )

        frontend_context_variables = self.component.get_frontend_context_variables()
        frontend_context_variables_dict = orjson.loads(frontend_context_variables)
        checksum = generate_checksum(str(frontend_context_variables_dict))

        # Use `html.parser` and not `lxml` because in testing it was no faster even with `cchardet`
        # despite https://thehftguy.com/2020/07/28/making-beautifulsoup-parsing-10-times-faster/
        soup = BeautifulSoup(content, features="html.parser")
        root_element = get_root_element(soup)
        root_element["unicorn:id"] = self.component.component_id
        root_element["unicorn:name"] = self.component.component_name
        root_element["unicorn:key"] = self.component.component_key
        root_element["unicorn:checksum"] = checksum

        # Generate the hash based on the rendered content (without script tag)
        hash = generate_checksum(UnicornTemplateResponse._desoupify(soup))

        if self.init_js:
            init = {
                "id": self.component.component_id,
                "name": self.component.component_name,
                "key": self.component.component_key,
                "data": orjson.loads(frontend_context_variables),
                "calls": self.component.calls,
                "hash": hash,
            }
            init = orjson.dumps(init).decode("utf-8")
            json_element_id = f"unicorn:data:{self.component.component_id}"
            init_script = f"Unicorn.componentInit(JSON.parse(document.getElementById('{json_element_id}').textContent));"

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
                script_tag.string = f"if (typeof Unicorn === 'undefined') {{ console.error('Unicorn is missing. Do you need {{% load unicorn %}} or {{% unicorn_scripts %}}?') }} else {{ {init_script} }}"

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


def get_root_element(soup: BeautifulSoup) -> Tag:
    """
    Gets the first tag element for the component or the first element with a `unicorn:view` attribute for a direct view.

    Returns:
        BeautifulSoup tag element.

        Raises `Exception` if an element cannot be found.
    """

    for element in soup.contents:
        if isinstance(element, Tag) and element.name:
            if element.name == "html":
                view_element = element.find_next(
                    attrs={"unicorn:view": True}
                ) or element.find_next(attrs={"u:view": True})

                if not view_element:
                    raise MissingComponentViewElement(
                        "An element with an `unicorn:view` attribute is required for a direct view"
                    )

                return view_element

            return element

    raise MissingComponentElement("No root element for the component was found")
