from django_unicorn.components import UnicornView


class Step1View(UnicornView):
    name: str
    email: str

    def mount(self):
        self.name = "Test"
        self.email = "test@example.com"

    def noop(self):
        print("no-op")
