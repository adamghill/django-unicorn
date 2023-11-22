from datetime import datetime

from django.utils import timezone

from django_unicorn.components import UnicornView


class TestDatetimeView(UnicornView):
    dt: datetime = None

    def mount(self):
        self.dt = timezone.now()

    def foo(self):
        pass
