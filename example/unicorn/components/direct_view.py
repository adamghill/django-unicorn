from django.utils.timezone import now

from django_unicorn.components import UnicornView


class DirectViewView(UnicornView):
    name = "test"
