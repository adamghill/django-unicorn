from django_unicorn.components import UnicornView
from example.coffee.models import Favorite


class FavoriteView(UnicornView):
    model: Favorite = None
    is_editing = False

    def updated(self, name, value):
        self.model.save()
        self.parent.is_updated_by_child = value
        self.parent.parent.favorite_count += 1 if value else -1
