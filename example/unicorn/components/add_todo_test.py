from django_unicorn.components import UnicornView
from django_unicorn.db import DbModel
from example.todos.models import Todo


class AddTodoTestView(UnicornView):
    class Meta:
        db_models = [DbModel("todo", Todo)]

    def save(self):
        print("A new book will be created automatically")
        pass
