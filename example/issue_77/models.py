from django.db import models


class ObjA(models.Model):
    name = models.CharField(max_length=42)


class ObjB(models.Model):
    name = models.CharField(max_length=42)


class ObjC(models.Model):
    relA = models.ForeignKey(ObjA, on_delete=models.CASCADE, related_name="objcs")
    relB = models.ForeignKey(ObjB, on_delete=models.CASCADE, related_name="objcs")
    value = models.FloatField()
