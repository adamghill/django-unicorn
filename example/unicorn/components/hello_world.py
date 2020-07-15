from django_unicorn.components import Component


class HelloWorld(Component):
    name = "World"
    is_checked = False
    thing = "🐙"
    things = [
        "alien",
    ]
    pie = "cherry"
    paragraph = ""
    state = ""

    def render(self, *args, **kwargs):
        template_context = {"component_name": "hello-world.html"}
        return super().render(template_context=template_context, *args, **kwargs)

    def states(self):
        if not self.state:
            return []

        return filter(
            lambda s: s.lower().startswith(self.state.lower()), self.all_states
        )

    all_states = (
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

    class Meta:
        exclude = ("all_states",)
