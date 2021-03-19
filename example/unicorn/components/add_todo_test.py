from django_unicorn.components import UnicornView
from django_unicorn.db import DbModel
from example.todos.models import Todo


class AddTodoTestView(UnicornView):
    todos = Todo.objects.none()

    def hydrate(self):
        self.todos = Todo.objects.all()

    def save(self):
        print("A new todo will be created automatically")

    class Meta:
        db_models = [DbModel("todo", Todo)]
