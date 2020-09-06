from django_unicorn.components import UnicornView

from django.utils.timezone import now


class PollingView(UnicornView):
    date_example = now()

    def get_date(self):
        self.date_example = now()
