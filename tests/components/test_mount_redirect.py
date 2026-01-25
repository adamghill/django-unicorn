from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.test import RequestFactory

from django_unicorn.components.unicorn_view import UnicornView, construct_component


class RedirectView(UnicornView):
    def mount(self):
        return redirect("/somewhere-else")


class ResponseView(UnicornView):
    def mount(self):
        return HttpResponse("Custom Content")


def test_mount_redirect_direct_view():
    request = RequestFactory().get("/")
    view = RedirectView.as_view()
    response = view(request)

    assert isinstance(response, HttpResponseRedirect)
    assert response.url == "/somewhere-else"


def test_mount_response_direct_view():
    request = RequestFactory().get("/")
    view = ResponseView.as_view()
    response = view(request)

    assert response.status_code == 200
    assert response.content.decode() == "Custom Content"


def test_mount_redirect_template_tag():
    # For now, let's verify construct_component captures it (once implemented)
    component = construct_component(RedirectView, "123", "test", "", None, None, [])

    # This attribute doesn't exist yet, but it's part of the plan
    assert hasattr(component, "_mount_result")
    assert isinstance(component._mount_result, HttpResponseRedirect)
    assert component._mount_result.url == "/somewhere-else"


def test_render_redirect_template_tag():
    component = construct_component(RedirectView, "123", "test", "", None, None, [])
    html = component.render()

    # Should be a script tag with generic redirect
    assert "<script>" in html
    assert "window.location.href = '/somewhere-else'" in html
