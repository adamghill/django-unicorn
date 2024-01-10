from django_unicorn.components import UnicornView


class Step2View(UnicornView):
    address: str
    city: str
    state: str
    zip_code: str

    def mount(self):
        self.address = "123 Main St"
        self.city = "Anytown"
        self.state = "CA"
        self.zip_code = "12345"
