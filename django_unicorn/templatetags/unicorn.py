from django import template

from ..components import get_component_class


register = template.Library()


@register.inclusion_tag("unicorn/scripts.html")
def unicorn_scripts():
    return {}


@register.inclusion_tag("unicorn/styles.html")
def unicorn_styles():
    return {}


def unicorn(parser, token):
    try:
        (tag_name, component_name) = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )

    if not (
        component_name[0] == component_name[-1] and component_name[0] in ('"', "'")
    ):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )

    return UnicornNode(component_name[1:-1])


class UnicornNode(template.Node):
    def __init__(self, component_name):
        self.component_name = component_name

    def render(self, context):
        Component = get_component_class(self.component_name)
        component = Component()
        rendered_component = component.render(self.component_name)

        return rendered_component


register.tag("unicorn", unicorn)
