from django_unicorn.components import Component


class HelloWorld(Component):
    name = "World"
    is_checked = False
    thing = "🐙"
    things = [
        "👾",
    ]
