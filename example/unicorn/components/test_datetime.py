from datetime import datetime
from typing import Optional

from django.utils import timezone

from django_unicorn.components import UnicornView


class TestDatetimeView(UnicornView):
    dt: Optional[datetime] = None

    def mount(self):
        self.dt = timezone.now()

    def foo(self):
        pass
