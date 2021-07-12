from django_unicorn.components import QuerySetType, UnicornView
from example.coffee.models import Flavor, Taste

class AddFlavorView(UnicornView):
    flavor_id = None
    is_adding = False
    flavor_obj = None
    flavor_qty = 1

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        self.flavor_id = kwargs.get('flavor_id')
        self.is_adding = False


    def create(self):

        if int(self.flavor_qty) > 0:
            for i in range(int(self.flavor_qty)):

                flavor = Flavor(
                    flavor = Flavor.objects.get(id = 1)
                )
                flavor.save()
                print("create flavor")
        
        self.is_adding = False
        self.show_table()


    def add_flavor(self):
        self.is_adding = True
        self.show_table()

    def cancel(self):
        self.is_adding = False
        self.show_table()
       
    def show_table(self):
        self.flavor_obj = Flavor.objects.get(id = 1)

    def mount(self):
        self.show_table()