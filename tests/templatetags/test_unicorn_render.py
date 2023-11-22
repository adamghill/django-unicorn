import re

import pytest
from django.template import Context
from django.template.base import Parser, Token, TokenType

from django_unicorn.components import UnicornView
from django_unicorn.errors import ComponentNotValidError
from django_unicorn.templatetags.unicorn import unicorn
from django_unicorn.utils import generate_checksum
from example.coffee.models import Flavor


class FakeModel:
    # Fake a model that only has an id

    def __init__(self):
        self.id = 178

    def to_json(self):
        return {"id": self.id}


class FakeComponent(UnicornView):
    template_name = "templates/test_component.html"


class FakeComponentParent(UnicornView):
    template_name = "templates/test_component_parent.html"


class FakeComponentParentImplicit(UnicornView):
    template_name = "templates/test_component_parent_implicit.html"


class FakeComponentChild(UnicornView):
    template_name = "templates/test_component_child.html"


class FakeComponentChildImplicit(UnicornView):
    template_name = "templates/test_component_child_implicit.html"

    def has_parent(self):
        return self.parent is not None


class FakeComponentArgs(UnicornView):
    template_name = "templates/test_component_args.html"
    hello = "world"

    def mount(self):
        self.hello = self.component_args[0]


class FakeComponentKwargs(UnicornView):
    template_name = "templates/test_component_kwargs.html"
    hello = "world"

    def mount(self):
        self.hello = self.component_kwargs.get("test_kwarg")


class FakeComponentKwargsWithHtmlEntity(UnicornView):
    template_name = "templates/test_component_kwargs_with_html_entity.html"
    hello = "world"

    def mount(self):
        self.hello = self.component_kwargs.get("test_kwarg")


class FakeComponentModel(UnicornView):
    template_name = "templates/test_component_model.html"
    model_id = None

    def mount(self):
        self.model_id = self.component_kwargs.get("model_id")


class FakeComponentCalls(UnicornView):
    template_name = "templates/test_component.html"

    def mount(self):
        self.call("testCall")


class FakeComponentCalls2(UnicornView):
    template_name = "templates/test_component.html"

    def mount(self):
        self.call("testCall2", "hello")


def test_unicorn_template_renders(client):
    response = client.get("/test")
    content = response.rendered_content.strip()

    assert response.wsgi_request.path == "/test"
    assert "WSGIRequest" in content
    assert content.startswith("<div unicorn:id")
    assert 'unicorn:name="tests.templatetags.test_unicorn_render.FakeComponentKwargs"' in content
    assert '<script type="application/json" id="unicorn:data:' in content


def test_unicorn_template_renders_with_parent_and_child(client):
    response = client.get("/test-parent")
    content = response.content.decode().strip()

    assert response.wsgi_request.path == "/test-parent"
    assert content.startswith("<div unicorn:id")
    assert 'unicorn:name="tests.templatetags.test_unicorn_render.FakeComponentParent"' in content
    assert 'unicorn:name="tests.templatetags.test_unicorn_render.FakeComponentChild"' in content
    assert "--parent--" in content
    assert "==child==" in content
    assert '<script type="application/json" id="unicorn:data:' in content


def test_unicorn_template_renders_with_parent_and_child_with_templateview(client):
    response = client.get("/test-parent-template")
    content = response.content.decode().strip()

    assert response.wsgi_request.path == "/test-parent-template"
    assert content.startswith("<div unicorn:id")
    assert 'unicorn:name="tests.templatetags.test_unicorn_render.FakeComponentParent"' in content
    assert 'unicorn:name="tests.templatetags.test_unicorn_render.FakeComponentChild"' in content
    assert "--parent--" in content
    assert "==child==" in content
    assert '<script type="application/json" id="unicorn:data:' in content


def test_unicorn_template_renders_with_implicit_parent_and_child(client):
    response = client.get("/test-parent-implicit")
    content = response.content.decode().strip()

    assert response.wsgi_request.path == "/test-parent-implicit"
    assert content.startswith("<div unicorn:id")
    assert 'unicorn:name="tests.templatetags.test_unicorn_render.FakeComponentParentImplicit"' in content
    assert 'unicorn:name="tests.templatetags.test_unicorn_render.FakeComponentChildImplicit"' in content
    assert "--parent--" in content
    assert "==child==" in content
    assert "has_parent:True" in content
    assert '<script type="application/json" id="unicorn:data:' in content


def test_unicorn_render_arg():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentArgs' 'tested!'",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {}
    actual = unicorn_node.render(Context(context))

    assert "<b>tested!</b>" in actual


def test_unicorn_render_kwarg():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' test_kwarg='tested!'",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {}
    actual = unicorn_node.render(Context(context))

    assert "<b>tested!</b>" in actual


def test_unicorn_render_context_variable():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' test_kwarg=test_var.nested",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {"test_var": {"nested": "variable!"}}
    actual = unicorn_node.render(Context(context))

    assert "<b>variable!</b>" in actual


def test_unicorn_render_with_invalid_html():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargsWithHtmlEntity' test_kwarg=test_var.nested",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {"test_var": {"nested": "variable!"}}
    actual = unicorn_node.render(Context(context))

    assert "-&gt;variable!&lt;-" in actual


def test_unicorn_render_parent(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view",
    )
    unicorn_node = unicorn(Parser([]), token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(Context(context))

    assert unicorn_node.parent
    assert unicorn_node.component_id == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs"


def test_unicorn_render_parent_with_key(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view key='blob'",
    )
    unicorn_node = unicorn(Parser([]), token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(Context(context))

    assert unicorn_node.component_id == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:blob"


def test_unicorn_render_parent_with_id(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view id='flob'",
    )
    unicorn_node = unicorn(Parser([]), token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(Context(context))

    assert unicorn_node.component_id == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:flob"


def test_unicorn_render_parent_with_pk(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view pk=99",
    )
    unicorn_node = unicorn(Parser([]), token)
    view = FakeComponentParent(component_name="test", component_id="asdf")
    context = {"view": view}
    unicorn_node.render(Context(context))

    assert unicorn_node.component_id == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:99"


def test_unicorn_render_parent_with_model_id(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view model=model",
    )
    unicorn_node = unicorn(Parser([]), token)
    view = FakeComponentParent(component_name="test", component_id="asdf")

    context = {"view": view, "model": FakeModel()}
    unicorn_node.render(Context(context))

    assert unicorn_node.component_id == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:178"


@pytest.mark.django_db
def test_unicorn_render_parent_with_model_pk(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view model=model",
    )
    unicorn_node = unicorn(Parser([]), token)
    view = FakeComponentParent(component_name="test", component_id="asdf")

    flavor = Flavor(pk=187)

    context = {"view": view, "model": flavor}
    unicorn_node.render(Context(context))

    assert unicorn_node.component_id == "asdf:tests.templatetags.test_unicorn_render.FakeComponentKwargs:187"


def test_unicorn_render_id_use_pk():
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentModel' model_id=model.id",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {"model": {"pk": 123}}
    actual = unicorn_node.render(Context(context))

    assert "==123==" in actual


def test_unicorn_render_component_one_script_tag(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs'",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1


def test_unicorn_render_component_minify_html(settings):
    settings.DEBUG = True
    settings.UNICORN["MINIFY_HTML"] = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs'",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert "<script type=module" in html
    assert len(re.findall("<script type=module", html)) == 1

    settings.UNICORN["MINIFY_HTML"] = False


def test_unicorn_render_child_component_no_script_tag(settings):
    settings.DEBUG = True
    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentKwargs' parent=view",
    )
    unicorn_node = unicorn(Parser([]), token)
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
    unicorn_node = unicorn(Parser([]), token)
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
    unicorn_node = unicorn(Parser([]), token)
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
    unicorn_node = unicorn(Parser([]), token)
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
    unicorn_node = unicorn(Parser([]), token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1
    assert '"calls":[]' in html


def test_unicorn_render_hash(settings):
    settings.DEBUG = True
    settings.UNICORN["SCRIPT_LOCATION"] = "after"

    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentParent'",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1
    assert '"hash":"' in html

    # Assert that the content hash is correct
    script_idx = html.index("<script")
    rendered_content_without_inserted_after_script = html[:script_idx]
    expected_hash = generate_checksum(rendered_content_without_inserted_after_script)
    assert f'"hash":"{expected_hash}"' in html


def test_unicorn_render_hash_append(settings):
    settings.DEBUG = True
    settings.UNICORN["SCRIPT_LOCATION"] = "append"

    token = Token(
        TokenType.TEXT,
        "unicorn 'tests.templatetags.test_unicorn_render.FakeComponentParent'",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1
    assert '"hash":"' in html

    # Assert that the content hash is correct
    script_idx = html.index("<script")
    rendered_content_without_appended_script = html[:script_idx] + "</div>"
    expected_hash = generate_checksum(rendered_content_without_appended_script)
    assert f'"hash":"{expected_hash}"' in html


def test_unicorn_render_with_component_name_from_context():
    token = Token(
        TokenType.TEXT,
        "unicorn component_name",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {"component_name": "tests.templatetags.test_unicorn_render.FakeComponent"}
    html = unicorn_node.render(Context(context))

    assert '<script type="module"' in html
    assert len(re.findall('<script type="module"', html)) == 1


def test_unicorn_render_with_invalid_component_name_from_context():
    token = Token(
        TokenType.TEXT,
        "unicorn bad_component_name",
    )
    unicorn_node = unicorn(Parser([]), token)
    context = {"component_name": "tests.templatetags.test_unicorn_render.FakeComponent"}

    with pytest.raises(ComponentNotValidError) as e:
        unicorn_node.render(Context(context))

    assert (
        e.exconly()
        == "django_unicorn.errors.ComponentNotValidError: Component template is not valid: bad_component_name."
    )
