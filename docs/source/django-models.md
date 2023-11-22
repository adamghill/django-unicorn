# Django Models

`Unicorn` provides tight integration with Django `Models` and `QuerySets` to handle typical workflows.

## Model

A Django `Model` can be used as a field on a component just like basic Python primitive types. Use `unicorn:model` to bind to a field of a Django `Model` like you would in a normal Django template.

:::{warning}
Using this functionality will serialize your entire model by default and expose all of the values in the HTML source code. Do not use this particular functionality if there are properties that need to be kept private.

One option is to customize the serialization of the model into a dictionary to only expose the data that should be publicly available.

Another option is to use [Meta.exclude](views.md#exclude) or [Meta.javascript_exclude](views.md#javascript_exclude) so those fields are not exposed.
:::

:::{code} html
:force: true

<!-- model.html -->
<div>
  <input unicorn:model.defer="book.title" type="text" id="book" />
  {{ book.title }}
  <button unicorn:click="save({{ book.pk }})">Save</button>
</div>
:::

```python
# model.py
from django_unicorn.components import UnicornView
from books.models import Book

class ModelView(UnicornView):
    book: Book = None

    def mount(self):
      self.book = Book.objects.all().first()

    def save(self, book_to_save: Book):
        book_to_save.save()
```

```{note}

The model's `pk` will be used to look up the correct model if there is only one argument for an action method and it has a type annotation for a Django `Model`. To lookup by a different model field, pass a dictionary into the front-end.

:::{code} html
:force: true
<button unicorn:click="delete({ 'uuid': '{{ book.uuid }}'})">Delete by uuid</button>
:::

:::{code} python
def delete(self, book_to_delete: Book):
    book_to_delete.delete()
:::

```

## QuerySet

Django models in a `QuerySet` can be accessed in a `unicorn:model` with "dot notation" similar to a `list`.

```python
# hello_world.py
from django_unicorn.components import UnicornView
from book.models import Book

class HelloWorldView(UnicornView):
    books = Book.objects.none()

    def mount(self):
        self.books = Book.objects.all()
```

```html
<!-- hello-world.html -->
<div>
  <input unicorn:model="books.0.title" type="text" id="text" />
</div>
```

An example of looping over all models in a queryset.

```python
# queryset.py
from django_unicorn.components import UnicornView
from books.models import Book

class QuerysetView(UnicornView):
    books = Book.objects.none()

    def mount(self):
        self.books = Book.objects.all().order_by("-id")[:5]

    def save(self, book_idx: int):
        self.books[book_idx].save()
```

:::{code} html
:force: true

<!-- queryset.html -->
<div>
  {% for book in books %}
  <div>
    <div>
      <input unicorn:model.defer="books.{{ forloop.counter0 }}.title" type="text" id="title" />
      {{ book.title }}
    </div>
    <div>
      <input unicorn:model.defer="books.{{ forloop.counter0 }}.description" type="text" id="description" />
      {{ book.description }}
    </div>
    <div>
      <button unicorn:click="save({{ forloop.counter0 }})">Save</button>
    </div>
  </div>
  {% endfor %}
</div>
:::

:::{warning}

This will expose all of the model values for the `QuerySet` in the HTML source. One way to avoid leaking all model information is to pass the fields that are publicly viewable into `values()` on your `QuerySet`.

```python
# queryset.py
from django_unicorn.components import UnicornView
from books.models import Book

class QuerysetView(UnicornView):
    books = Book.objects.none()

    def mount(self):
      self.books = Book.objects.all().order_by("-id").values("pk", "title")
```

:::

A `QuerySetType` type hint can be used to ensure the correct `QuerySet` is used for the component field.

```python
# queryset.py
from django_unicorn.components import QuerySetType, UnicornView
from books.models import Book

class QuerysetView(UnicornView):
    books: QuerySetType[Book] = None

    def mount(self):
        self.books = Book.objects.all().order_by("-id")[:5]

    def save(self, book_idx: int):
        self.books[book_idx].save()
```
