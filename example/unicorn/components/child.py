from datetime import datetime
from django_unicorn.components import UnicornView

class ChildView(UnicornView):
    def foo(self):
        print("child clicked, calling parent's foo()")
        self.parent.foo()
