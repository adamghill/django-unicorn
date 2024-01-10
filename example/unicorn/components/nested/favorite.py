from django_unicorn.components import UnicornView
from example.coffee.models import Favorite


class FavoriteView(UnicornView):
    model: Favorite = None
    is_editing = False

    def updated(self, name, value):
        if not self.model:
            self.model = Favorite(flavor_id=self.parent.model.id, is_favorite=value)

        self.model.save()
        self.parent.is_updated_by_child = value
        self.parent.parent.favorite_count += 1 if value else -1

        self.parent.parent.force_render = True
