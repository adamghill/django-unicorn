from django_unicorn.components import UnicornView
from example.coffee.models import Favorite


class FavoriteView(UnicornView):
    model: Favorite = None  # type: ignore
    is_editing = False

    def updated(self, name, value):
        if not self.model:
            self.model = Favorite(flavor_id=self.parent.model.id, is_favorite=value)  # type: ignore

        self.model.save()
        self.parent.is_updated_by_child = value  # type: ignore
        self.parent.parent.favorite_count += 1 if value else -1  # type: ignore

        self.parent.parent.force_render = True  # type: ignore
