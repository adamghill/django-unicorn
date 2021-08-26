import logging

from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe

import orjson
from bs4 import BeautifulSoup
from bs4.element import Tag
from bs4.formatter import HTMLFormatter

from django_unicorn.utils import sanitize_html

from ..decorators import timed
from ..utils import generate_checksum


logger = logging.getLogger(__name__)


class UnsortedAttributes(HTMLFormatter):
    """
    Prevent beautifulsoup from re-ordering attributes.
    """

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

        frontend_context_variables = self.component.get_frontend_context_variables()
        frontend_context_variables_dict = orjson.loads(frontend_context_variables)
        checksum = generate_checksum(orjson.dumps(frontend_context_variables_dict))

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

            # Include init script and json tags from child components
            json_tags = [json_tag]
            for child in self.component.children:
                init_script = f"{init_script} {child._init_script}"
                json_tags.extend(child._json_tags)

            # Defer rendering the init script and json tag until the outermost
            # component (without a parent) is rendered
            if self.component.parent:
                self.component._init_script = init_script
                self.component._json_tags = json_tags
            else:
                script_tag = soup.new_tag("script")
                script_tag["type"] = "module"
                script_tag.string = f"if (typeof Unicorn === 'undefined') {{ console.error('Unicorn is missing. Do you need {{% load unicorn %}} or {{% unicorn_scripts %}}?') }} else {{ {init_script} }}"
                root_element.insert_after(script_tag)

                for t in json_tags:
                    root_element.insert_after(t)

        rendered_template = UnicornTemplateResponse._desoupify(soup)
        rendered_template = mark_safe(rendered_template)
        self.component.rendered(rendered_template)

        response.content = rendered_template

        return response

    @staticmethod
    def _desoupify(soup):
        soup.smooth()
        return soup.encode(formatter=UnsortedAttributes()).decode("utf-8")


def get_root_element(soup: BeautifulSoup) -> Tag:
    """
    Gets the first tag element.

    Returns:
        BeautifulSoup tag element.

        Raises an Exception if an element cannot be found.
    """
    for element in soup.contents:
        if isinstance(element, Tag) and element.name:
            return element

    raise Exception("No root element found")
