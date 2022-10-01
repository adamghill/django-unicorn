# Components

`Unicorn` uses the term "component" to refer to a set of interactive functionality that can be put into templates. A component consists of a Django HTML `template` with specific tags and a Python `view` class which provides the backend code for the template.

## Create a component

The easiest way to create your first component is to run the `startunicorn` Django management command after `Unicorn` is installed.

The first argument to `startunicorn` is the Django app to add your component to. Every argument after is a new component to create a template and view for.

```shell
# Create `hello-world` and `hello-magic` components in a `unicorn` app
python manage.py startunicorn unicorn hello-world hello-magic
```

```{warning}
If the app does not already exist, `startunicorn` will ask if it should call `startapp` to create a new application. However, make sure to add the app name to `INSTALLED_APPS` in your Django settings file (normally `settings.py`). Otherwise Django will not be able to find the newly created component templates.
```

```{note}
Explicitly set which apps `Unicorn` looks in for components with the [APPS setting](settings.md#apps). Otherwise, all `INSTALLED_APPS` will be searched for components.
```

Then, add a `{% unicorn 'hello-world' %}` templatetag into the template where you want to load the new component.

```{warning}
Make sure that there is a `{% csrf_token %}` rendered by the HTML template that includes the component to prevent cross-site scripting attacks while using `Unicorn`.
```

## Component key

If there are multiple of the same components on the page, a `key` kwarg can be passed into the template. For example, `{% unicorn 'hello-world' key='helloWorldKey' %}`. This is useful when a unique reference to a component is required, but it is optional.

## Component arguments

`kwargs` can be passed into the `unicorn` templatetag from the template. The `kwargs` will be available in the component [`__init__`](advanced.md#__init__) method.

```{warning}
When overriding `__init__` calling `super().__init__(**kwargs)` is required for the component to initialize properly.
```

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    name = "World"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)  # calling super is required
        self.name = kwargs.get("name")
```

```html
<!-- index.html -->
{% unicorn 'hello-world' name="Universe" %}
```

Regular Django template variables can also be passed in as an argument as long as it is available in the template context.

```python
# views.py
from django.shortcuts import render

def index(request):
    context = {"hello": {"world": {"name": "Galaxy"}}}
    return render(request, "index.html", context)
```

```html
<!-- index.html -->
{% unicorn 'hello-world' name=hello.world.name %}
```

## Example component

A basic example component could consist of the following template and class.

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    name = "World"
```

```html
<!-- hello-world.html -->
<div>
  <input unicorn:model="name" type="text" id="text" /><br />
  Hello {{ name|title }}
</div>
```

`unicorn:model` is the magic that ties the input to the backend component. The Django template variable can use any property or method on the component as if they were context variables passed in from a view. The attribute passed into `unicorn:model` refers to the property in the component class and binds them together.

```{note}
By default `unicorn:model` updates are triggered by listening to `input` events on the element. To listen for the `blur` event instead, use the [lazy](templates.md#lazy) modifier.
```

When a user types into the text input, the information is passed to the backend and populates the component class, which is then used to generate the output of the template HTML. The template can use any normal Django templatetags or filters (e.g. the `title` filter above).

## Component sub-folders

Components can also be nested in sub-folders.

```
unicorn/
    components/
        __init__.py
        hello/
            __init__.py
            world.py
    templates/
        unicorn/
            hello/
                world.html
```

An example of how the above component would be included in a template.

```html
<!-- index.html -->
{% unicorn 'hello.world' %}
```

## Unicorn attributes

Attributes used in component templates usually start with `unicorn:`, however the shortcut `u:` is also supported. So, for example, `unicorn:model` could also be written as `u:model`.

## Supported property types

Properties of the component can be of many different types, including `str`, `int`, `list`, `dictionary`, `Decimal`,[`Django Model`](django-models.md#model), [`Django QuerySet`](django-models.md#queryset), [`dataclass`](https://docs.python.org/3.7/library/dataclasses.html), or `custom classes`.

### Property type hints

`Unicorn` will attempt to cast any properties with a `type hint` when the component is hydrated.

```python
# rating.py
from django_unicorn.components import UnicornView

class RatingView(UnicornView):
    rating: float = 0

    def calculate_percentage(self):
        print(self.rating / 100.0)
```

Without `rating: float`, when `calculate_percentage` is called Python will complain with an error message like the following.

```shell
TypeError: unsupported operand type(s) for /: 'str' and 'int'`
```

### Accessing nested fields

Fields in a `dictionary` or Django model can be accessed similarly to the Django template language with "dot-notation".

```python
# hello_world.py
from django_unicorn.components import UnicornView
from book.models import Book

class HelloWorldView(UnicornView):
    book = Book.objects.get(title='American Gods')
    book_ratings = {'excellent': {'title': 'American Gods'}}
```

```html
<!-- hello-world.html -->
<div>
  <input unicorn:model="book.title" type="text" id="model" />
  <input
    unicorn:model="book_ratings.excellent.title"
    type="text"
    id="dictionary"
  />
</div>
```

```{note}
[Django models](django-models.md) has many more details about using Django models in `Unicorn`.
```

### Django QuerySet

`Django QuerySet` can be referenced similarly to the Django template language in a `unicorn:model`.

```python
# hello_world.py
from django_unicorn.components import UnicornView
from book.models import Book

class HelloWorldView(UnicornView):
    books = Book.objects.all()
```

```html
<!-- hello-world.html -->
<div>
  <input unicorn:model="books.0.title" type="text" id="text" />
</div>
```

```{note}
[Django models](django-models.md#queryset) has many more details about using Django QuerySets in `Unicorn`.
```

### Custom class

Custom classes need to define how they are serialized. If you have access to the object to serialize, you can define a `to_json` method on the object to return a dictionary that can be used to serialize. Inheriting from `unicorn.components.UnicornField` is a quick way to serialize a custom class, but note that it just calls `self.__dict__` under the hood, so it is not doing anything particularly smart.

Another option is to set the `form_class` on the component and utilize Django's built-in forms and widgets to handle how the class should be deserialized. More details are provided in [validation](validation.md).

```python
# hello_world.py
from django_unicorn.components import UnicornView, UnicornField

class Author(UnicornField):
    def __init__(self):
        self.name = 'Neil Gaiman'

    # Not needed because inherited from `UnicornField`
    # def to_json(self):
    #    return {'name': self.name}

    class HelloWorldView(UnicornView):
        author = Author()
```

```html
<!-- hello-world.html -->
<div>
  <input unicorn:model="author.name" type="text" id="author_name" />
</div>
```

```{danger}
Never put sensitive data into a public property because that information will publicly available in the HTML source code, unless explicitly prevented with [`javascript_exclude`](advanced.md#javascript_exclude).
```
