from typing import Dict

from django import template
from django.conf import settings

import shortuuid

from django_unicorn.call_method_parser import InvalidKwarg, parse_kwarg

from ..settings import get_setting


register = template.Library()


@register.inclusion_tag("unicorn/scripts.html")
def unicorn_scripts():
    return {"MINIFIED": get_setting("MINIFIED", not settings.DEBUG)}


@register.inclusion_tag("unicorn/errors.html", takes_context=True)
def unicorn_errors(context):
    return {"unicorn": {"errors": context.get("unicorn", {}).get("errors", {})}}


def unicorn(parser, token):
    contents = token.split_contents()

    if len(contents) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires at least a single argument" % token.contents.split()[0]
        )

    tag_name = contents[0]
    component_name = contents[1]

    if not (
        component_name[0] == component_name[-1] and component_name[0] in ('"', "'")
    ):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )

    kwargs = {}

    for arg in contents[2:]:
        try:
            kwarg = parse_kwarg(arg)
            kwargs.update(kwarg)
        except InvalidKwarg:
            pass

    return UnicornNode(component_name[1:-1], kwargs)


class UnicornNode(template.Node):
    def __init__(self, component_name: str, kwargs: Dict = {}):
        self.component_name = component_name
        self.kwargs = kwargs
        self.component_key = ""
        self.parent = None

    def render(self, context):
        request = None

        if hasattr(context, "request"):
            request = context.request

        component_id = shortuuid.uuid()[:8]

        resolved_kwargs = {}

        for key, val in self.kwargs.items():
            try:
                resolved_kwargs.update({key: template.Variable(val).resolve(context)})
            except TypeError:
                resolved_kwargs.update({key: val})
            except template.VariableDoesNotExist:
                resolved_kwargs.update({key: val})

        if "key" in resolved_kwargs:
            self.component_key = resolved_kwargs.pop("key")

        if "parent" in resolved_kwargs:
            self.parent = resolved_kwargs.pop("parent")

        from ..components import UnicornView

        view = UnicornView.create(
            component_id=component_id,
            component_name=self.component_name,
            component_key=self.component_key,
            parent=self.parent,
            kwargs=resolved_kwargs,
            request=request,
        )
        rendered_component = view.render(init_js=True)

        return rendered_component


register.tag("unicorn", unicorn)
