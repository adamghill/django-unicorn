from datetime import datetime
from django.utils import timezone
from django_unicorn.components import UnicornView

class ParentView(UnicornView):
    def mount(self):
        print("parent mount: request=", self.request)


    def foo(self):
        print("parent click: request=", self.request)
