from django.http.response import Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist


def index(request):
    return render(request, "www/index.html")


def template(request, name):
    try:
        return render(request, f"www/{name}.html", context={"example": "test"})
    except TemplateDoesNotExist:
        raise Http404
