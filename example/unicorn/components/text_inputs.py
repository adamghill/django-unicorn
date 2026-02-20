from django.utils.timezone import now

from django_unicorn.components import UnicornView


class TextInputsView(UnicornView):
    name = "World"
    testing_xss = "Whatever </script> <script>alert('uh oh')</script>"

    def set_name(self, name=None):
        if name:
            self.name = name
        else:
            self.name = "Universe"

        return f"{self.name} - {now().second}"
