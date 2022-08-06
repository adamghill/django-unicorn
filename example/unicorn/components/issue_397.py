from typing import Dict

from django_unicorn.components import UnicornView


class Issue397View(UnicornView):
    counter: int = 1
    counter2: Dict = None

    def mount(self):
        self.counter2 = {"more": 8}

    def inc(self):
        self.counter += 1
        self.counter2["more"] += 1

    def updated_counter(self, value):
        print(f"updated_counter: {value}")
    
    def updated_counter2(self, value):
        print(f"updated_counter2: {value}")

    def updated(self, name, value):
        print(f"updated: {name}, {value}")
