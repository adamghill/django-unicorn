from django.http.response import Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.views import generic


def index(request):
    return render(request, "www/index.html")


def template(request, name):
    try:
        return render(request, f"www/{name}.html", context={"example": "test"})
    except TemplateDoesNotExist:
        raise Http404

class ClassViewView(generic.TemplateView):
    template_name = "www/nested.html"

    def get_context_data(self, **kwargs):
        context = super(ClassViewView, self).get_context_data(**kwargs)

        context["example"] = "test"
        return context