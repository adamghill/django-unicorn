from django.shortcuts import redirect
from django.utils.timezone import now

from django_unicorn.components import HashUpdate, LocationUpdate, UnicornView


class RedirectsView(UnicornView):
    location_count: int = 0
    hash_count: int = 0
    redirect_count: int = 0

    def update_location(self):
        self.location_count += 1

        return LocationUpdate(
            redirect(f"/redirects#{self.location_count}"),
            title=f"{self.location_count}",
        )

    def update_hash(self):
        self.hash_count += 1

        return HashUpdate(f"#{self.hash_count}")

    def do_redirect(self):
        return redirect(f"/redirects#{now().timestamp()}")
