from django_unicorn.components import UnicornView, UnicornField

from books.models import Book


class Person(UnicornField):
    def __init__(self):
        self.gender = "male"


class Author(UnicornField):
    def __init__(self):
        self.name = "Neil Gaiman"
        self.person = Person()


class HelloWorldView(UnicornView):
    template_name = "unicorn/hello-world.html"

    name = "World"
    is_checked = False
    thing = "🐙"
    things = [
        "alien",
    ]
    pie = "cherry"
    paragraph = ""
    state = ""
    author = Author()
    dictionary = {"stuff": "here", "things": {"great": "yes"}}
    book = Book.objects.get(title="The Sandman")
    books = Book.objects.all()

    ALL_STATES = (
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
    )

    def set_name(self, name=None):
        if name:
            self.name = name
        else:
            self.name = "Universe"

    def clear_states(self):
        self.state = ""

    def states(self):
        if not self.state:
            return []

        return [s for s in self.ALL_STATES if s.lower().startswith(self.state.lower())]

    class Meta:
        exclude = ("ALL_STATES",)
