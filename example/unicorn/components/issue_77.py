from issue_77.models import ObjA, ObjB, ObjC

from django_unicorn.components import UnicornView


class Issue77View(UnicornView):
    name = "uview"
    obja = None
    objc_left = None
    objc_right = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obja = ObjA.objects.get(pk=kwargs["pk"])

    def set_left(self, pk):
        print("OBJ L")
        print(pk)
        self.objc_left = ObjC.objects.get(pk=pk)
        print(self.objc_left)

    def set_right(self, pk):
        print("OBJ R")
        print(pk)
        self.objc_right = ObjC.objects.get(pk=pk)
        print(self.objc_right)