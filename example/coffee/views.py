from django.views import generic
from example.coffee.models import Flavor, Taste

class FlavorListView(generic.ListView):
    template_name = 'www/add-flavor.html'
    context_object_name = 'flavor_list'
    model = Flavor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flavor_list'] = Flavor.objects.all()
        return context