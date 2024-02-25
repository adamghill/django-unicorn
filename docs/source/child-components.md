# Child components

`Unicorn` supports nesting components so that one component is a child of another. Since HTML is a tree structure, a component can have multiple children, but each child only has one parent.

We will slowly build a nested component example with three components: `table`, `filter`, and `row`. The table is the parent and contains the other two components. The filter will update the parent table component, and the row will contain functionality to edit a row.

## Parent component

```html
<!-- table.html -->
{% load unicorn %}
<div>
  {% unicorn 'filter' %}

  <table>
    <thead>
      <tr>
        <td>Author</td>
        <td>Title</td>
      </tr>
    </thead>
    {% for book in books %}
    <tr>
      <td>{{ book.author }}</td>
      <td>{{ book.title }}</td>
    </tr>
    {% endfor %}
  </table>
</div>
```

```python
# table.py
from book.models import Book
from django_unicorn.components import UnicornView

class TableView(UnicornView):
    books = Book.objects.none()

    def mount(self):
        self.load_table()

    def load_table(self):
        self.books = Book.objects.all()[0:10]
```

## Child component

The child component, `filter`, will have access to its parent through the view's `self.parent`. The `FilterView` is using the [updated](https://www.django-unicorn.com/docs/advanced/#updated-property-name-value) method to filter the `books` queryset on the table component when the filter's `search` model is changed.

```html
<!-- filter.html -->
<div>
  <input type="text" unicorn:model="search" />
</div>
```

```python
from django_unicorn.components import UnicornView

class FilterView(UnicornView):
    search = ""

    def updated_search(self, query):
        self.parent.load_table()

        if query:
            self.parent.books = list(
                filter(lambda f: query.lower() in f.title.lower(), self.parent.books)
            )
        
        # Forces the parent to re-render instead of just the current component
        self.parent.force_render = True
```

## Multiple children

If we want to encapsulate the editing and saving of a row of data, we can add in a row component as well.

```{note}
The [discard](actions.md#discard) action modifier is used on the cancel button to provide an easy way to prevent any edits from being saved.
```

:::{code} html
:force: true

<!-- row.html -->
<tr>
  <td>
    {% if is_editing %}
    <input type="text" unicorn:model.defer="book.author" />
    {% else %}
    {{ book.author }}
    {% endif %}
  </td>
  <td>
    {% if is_editing %}
    <input type="text" unicorn:model.defer="book.title" />
    {% else %}
    {{ book.title }}
    {% endif %}
  </td>
  <td>
    {% if is_editing %}
    <button unicorn:click="save">Save</button>
    <button unicorn:click.discard="cancel">Cancel</button>
    {% else %}
    <button unicorn:click="edit">Edit</button>
    {% endif %}
  </td>
</tr>
:::

```python
# row.py
from django_unicorn.components import UnicornView

class RowView(UnicornView):
    book = None
    is_editing = False

    def edit(self):
        self.is_editing = True

    def cancel(self):
        self.is_editing = False

    def save(self):
        self.book.save()
        self.is_editing = False
```

The changes for the table component where the row child component is added in. Views will always have a `children` attribute -- here it is used to set `is_editing` to `false` on all rows when the table gets reloaded.

```html
<!-- table.html --->
{% load unicorn %}
<div>
  {% unicorn 'filter' %}

  <table>
    <thead>
      <tr>
        <td>Author</td>
        <td>Title</td>
      </tr>
    </thead>
    {% for book in books %}
    {% unicorn 'row' book=book key=book.id %}
    {% endfor %}
  </table>
</div>
```

```python
# table.py
from book.models import Book
from django_unicorn.components import UnicornView

class TableView(UnicornView):
    books = Book.objects.none()

    def mount(self):
        self.load_table()

    def load_table(self):
        self.books = Book.objects.all()

        for child in self.children:
            if hasattr(child, "is_editing"):
                child.is_editing = False
```

````{warning}
`Unicorn` requires components to have a unique identifier. Normally that is handled automatically, however multiple child components with the same component name require some help.

For child components, `unicorn:id` is automatically created from the parent's `unicorn:id` and the child's component name. If a child component is created multiple times in the same parent, one of the following can be used to create unique identifiers:

- pass in a `key` keyword argument to the child component
```html
{% unicorn 'row' book=book key=book.id %}
```
- pass in an `id` keyword argument to the child component
```html
{% unicorn 'row' book=book id=book.id %}
```
- the view has an attribute named `model` which has either a `pk` or `id` attribute
```html
{% unicorn 'row' model=book %}
```

````
