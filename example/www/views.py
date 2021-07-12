from django.http.response import Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.views import generic
from example.coffee.models import Flavor, Taste


# def index(request):
#     return render(request, "www/index.html")


# def template(request, name):
#     try:
#         return render(request, f"www/{name}.html", context={"example": "test"})
#     except TemplateDoesNotExist:
#         raise Http404



class FlavorListView(generic.ListView):
    template_name = 'www/add-flavor.html'
    context_object_name = 'flavor_list'
    model = Flavor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flavor_list'] = Flavor.objects.all()
        context['taste_list'] = Taste.objects.all()
        return context
