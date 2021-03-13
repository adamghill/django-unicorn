from django.db import models


class Todo(models.Model):
    description = models.CharField(max_length=50)
    is_completed = models.BooleanField(default=False, blank=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "todos"
