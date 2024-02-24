# Direct View

Usually components will be included in a regular Django template, however a component can also be specified in a `urls.py` file in instances where having an additional template is not necessary.

## Template Requirements

- there must be one (and only one) element that wraps around the portion of the template that should be handled by `Unicorn`
- the wrapping element must include `unicorn:view` as an attribute
- the template must included the `unicorn_scripts` and `csrf_token` template tags

Similar to a class-based view, `Unicorn` components have a `as_view` function which is used in `urls.py`.

## Example

```python
# book.py
from django_unicorn.components import UnicornView

class BookView(UnicornView):
    title = ""
```

```html
<!-- book.html -->
{% load unicorn %}

<html>
  <head>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}
    <h1>Book</h1>

    <div unicorn:view>
      <input unicorn:model="title" type="text" /><br />
      {{ title }}
    </div>
  </body>
</html>
```

```python
# urls.py
from django.urls import path
from unicorn.components.book import BookView

urlpatterns = [
    path("book", BookView.as_view(), name="book"),
]
```
