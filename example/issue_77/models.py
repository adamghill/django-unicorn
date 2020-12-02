from django.db import models


class ObjA(models.Model):
    name = models.CharField(max_length=42)


class ObjB(models.Model):
    name = models.CharField(max_length=42)


class ObjC(models.Model):
    relA = models.ForeignKey(ObjA, on_delete=models.CASCADE, related_name="objcs")
    relB = models.ForeignKey(ObjB, on_delete=models.CASCADE, related_name="objcs")
    value = models.FloatField()

def populate():
    print("POPULATE DATABASE FOR ISSUE 77")

    try:
        a1 = ObjA.objects.create(id=1, name="A_1")
    except:
        pass

    try:
        b1 = ObjB.objects.create(id=1, name="B_1")
    except:
        pass
    try:
        b2 = ObjB.objects.create(id=2, name="B_2")
    except:
        pass

    try:
        c1 = ObjC.objects.create(id=1, relA=a1, relB=b1, value=0)
    except:
        pass
    try:
        c2 = ObjC.objects.create(id=2, relA=a1, relB=b2, value=0)
    except:
        pass

    print(ObjA.objects.all())
    print(ObjB.objects.all())
    print(ObjC.objects.all())


#populate()