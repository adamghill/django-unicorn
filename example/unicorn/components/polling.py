from django.utils.timezone import now

from django_unicorn.components import UnicornView


class PollingView(UnicornView):
    date_example = now()

    def get_date(self):
        self.date_example = now()
