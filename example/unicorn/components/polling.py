from django.utils.timezone import now

from django_unicorn.components import UnicornView


class PollingView(UnicornView):
    polling_disabled = False
    date_example = now()
    current_time = now()

    def refresh(self):
        self.current_time = now()

    def get_date(self):
        self.date_example = now()
