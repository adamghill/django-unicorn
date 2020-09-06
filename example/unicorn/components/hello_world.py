from django_unicorn.components import UnicornView, UnicornField


class HelloWorldView(UnicornView):
    template_name = "unicorn/hello-world-test.html"

    name = "World"

    def set_name(self):
        self.name = "set_name method called"
