import time

from django.contrib import messages
from django.utils.timezone import now

from django_unicorn.components import PollUpdate, UnicornView


class PollingView(UnicornView):
    polling_disabled = False
    date_example = now()
    current_time = now()
    counter = 0

    def slow_update(self):
        self.counter += 1
        time.sleep(0.8)  # Simulate slow request

    def get_date(self):
        self.current_time = now()
        self.date_example = now()

        messages.error(self.request, "get_date called :(")

        return PollUpdate(timing=2000, disable=False, method="get_date_2")

    def get_date_2(self):
        self.current_time = now()
        self.date_example = now()

        messages.success(self.request, "get_date2 called :)")

        return PollUpdate(timing=1000, disable=False, method="get_date")
