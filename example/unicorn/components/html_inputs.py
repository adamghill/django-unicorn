from typing import Optional

from django_unicorn.components import UnicornView
from example.coffee.models import Flavor


class HtmlInputsView(UnicornView):
    is_checked = False
    another_check = True
    thing = "🐙"
    flavor: Optional[Flavor] = None
    flavors = Flavor.objects.none()
    things = [
        "alien",
    ]
    pie = "cherry"
    paragraph = ""
    state = ""

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

    def mount(self):
        self.flavors = Flavor.objects.all()[:3]

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
