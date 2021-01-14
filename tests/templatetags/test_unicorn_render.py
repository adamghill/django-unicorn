from django.template.base import Token, TokenType

from django_unicorn.components import UnicornView
from django_unicorn.templatetags.unicorn import unicorn


class FakeComponentParent(UnicornView):
    template_name = "templates/test_component_parent.html"


class FakeComponentKwargs(UnicornView):
    template_name = "templates/test_component_kwargs.html"
    hello = "world"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.hello = kwargs.get("test_kwarg")


def test_unicorn_render_kwarg():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' test_kwarg='tested!'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    actual = unicorn_node.render(context)

    assert "->tested!<-" in actual


def test_unicorn_render_context_variable():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' test_kwarg=test_var.nested",
    )
    unicorn_node = unicorn(None, token)
    context = {"test_var": {"nested": "variable!"}}
    actual = unicorn_node.render(context)

    assert "->variable!<-" in actual


def test_unicorn_render_parent():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(context)

    assert unicorn_node.parent
