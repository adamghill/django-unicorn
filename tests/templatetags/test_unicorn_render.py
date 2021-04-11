import re

from django.template import Context
from django.template.base import Token, TokenType

import pytest

from django_unicorn.components import UnicornView
from django_unicorn.templatetags.unicorn import unicorn
from django_unicorn.utils import generate_checksum
from example.coffee.models import Flavor


class FakeComponentParent(UnicornView):
    template_name = "templates/test_component_parent.html"


class FakeComponentKwargs(UnicornView):
    template_name = "templates/test_component_kwargs.html"
    hello = "world"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.hello = kwargs.get("test_kwarg")


class FakeComponentKwargsWithHtmlEntity(UnicornView):
    template_name = "templates/test_component_kwargs_with_html_entity.html"
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


class FakeComponentCalls(UnicornView):
    template_name = "templates/test_component_parent.html"

    def mount(self):
        self.call("testCall")


class FakeComponentCalls2(UnicornView):
    template_name = "templates/test_component_parent.html"

    def mount(self):
        self.call("testCall2", "hello")


def test_unicorn_has_context_processors_in_context(client):
    response = client.get("/test")
    assert "WSGIRequest" in response.content.decode()


def test_unicorn_render_kwarg():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' test_kwarg='tested!'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    actual = unicorn_node.render(Context(context))

    assert "<b>tested!</b>" in actual


def test_unicorn_render_context_variable():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' test_kwarg=test_var.nested",
    )
    unicorn_node = unicorn(None, token)
    context = {"test_var": {"nested": "variable!"}}
    actual = unicorn_node.render(Context(context))

    assert "<b>variable!</b>" in actual


def test_unicorn_render_with_invalid_html():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargsWithHtmlEntity' test_kwarg=test_var.nested",
    )
    unicorn_node = unicorn(None, token)
    context = {"test_var": {"nested": "variable!"}}
    actual = unicorn_node.render(Context(context))

    assert "-&gt;variable!&lt;-" in actual


def test_unicorn_render_parent(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(Context(context))

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
    unicorn_node.render(Context(context))

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
    unicorn_node.render(Context(context))

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
    unicorn_node.render(Context(context))

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
    unicorn_node.render(Context(context))

    assert (
        unicorn_node.component_id
        == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:178"
    )


@pytest.mark.django_db
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
    unicorn_node.render(Context(context))

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
    actual = unicorn_node.render(Context(context))

    assert "==123==" in actual


def test_unicorn_render_component_one_script_tag(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1


def test_unicorn_render_child_component_no_script_tag(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view",
    )
    unicorn_node = unicorn(None, token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    html = unicorn_node.render(Context(context))

    assert "<script" not in html


def test_unicorn_render_parent_component_one_script_tag(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentParent'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1


def test_unicorn_render_calls(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentCalls'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1
    assert '"calls":[{"fn":"testCall","args":[]}]' in html


def test_unicorn_render_calls_with_arg(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentCalls2'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1
    assert '"calls":[{"fn":"testCall2","args":["hello"]}]' in html


def test_unicorn_render_calls_no_mount_call(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentParent'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1
    assert '"calls":[]' in html


def test_unicorn_render_hash(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentParent'",
    )
    unicorn_node = unicorn(None, token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1
    assert '"hash":"' in html

    # Assert that the content hash is correct
    script_idx = html.index("<script")
    rendered_content = html[:script_idx]
    expected_hash = generate_checksum(rendered_content)
    assert f'"hash":"{expected_hash}"' in html
