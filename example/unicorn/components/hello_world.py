from django_unicorn.components import UnicornField, UnicornView


class HelloWorldView(UnicornView):
    template_name = "unicorn/hello-world-test.html"

    name = "World"

    def set_name(self):
        self.name = "set_name method called"
