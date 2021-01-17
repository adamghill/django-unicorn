from django.template.base import Token, TokenType

from django_unicorn.components import UnicornView
from django_unicorn.templatetags.unicorn import unicorn
from example.coffee.models import Flavor


class FakeComponentParent(UnicornView):
    template_name = "templates/test_component_parent.html"


class FakeComponentKwargs(UnicornView):
    template_name = "templates/test_component_kwargs.html"
    hello = "world"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.hello = kwargs.get("test_kwarg")


class FakeComponentModel(UnicornView):
    template_name = "templates/test_component_model.html"
    model_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.model_id = kwargs.get("model_id")


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


def test_unicorn_render_parent(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(context)

    assert unicorn_node.parent
    assert (
        unicorn_node.component_id
        == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs"
    )


def test_unicorn_render_parent_with_key(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view key='blob'",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(context)

    assert (
        unicorn_node.component_id
        == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:blob"
    )


def test_unicorn_render_parent_with_id(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view id='flob'",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(context)

    assert (
        unicorn_node.component_id
        == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:flob"
    )


def test_unicorn_render_parent_with_pk(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view pk=99",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(context)

    assert (
        unicorn_node.component_id
        == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:99"
    )


def test_unicorn_render_parent_with_model_id(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view model=model",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")

    # Fake a model that only has an id
    class Model:
        def __init__(self):
            self.id = 178

        def to_json(self):
            return {"id": self.id}

    context = {"view": view, "model": Model()}
    unicorn_node.render(context)

    assert (
        unicorn_node.component_id
        == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:178"
    )


def test_unicorn_render_parent_with_model_pk(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view model=model",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")

    flavor = Flavor(pk=187)
    context = {"view": view, "model": flavor}
    unicorn_node.render(context)

    assert (
        unicorn_node.component_id
        == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:187"
    )


def test_unicorn_render_id_use_pk():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentModel' model_id=model.id",
    )
    unicorn_node = unicorn(None, token)
    context = {"model": {"pk": 123}}
    actual = unicorn_node.render(context)

    assert "==123==" in actual
