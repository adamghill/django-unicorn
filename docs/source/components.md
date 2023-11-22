# Components

`Unicorn` uses the term "component" to refer to a set of interactive functionality. A component consists of a Python [`view`](views.md) class which provides the backend code and a Django HTML [`template`](templates.md).

## Create a component

The easiest way to create your first component is to run the `startunicorn` Django management command after `Unicorn` is installed.

The first argument to `startunicorn` is the Django app to add your component to. Every argument after the first is the name of a component to create.

```shell
# Create `hello-world` and `hello-magic` components in `myapp`
python manage.py startunicorn myapp hello-world hello-magic
```

That would create a file structure like the following:
```
myapp/
    components/
        __init__.py
        hello_world.py
        hello_magic.py
    templates/
        myapp/
            hello-world.html
            hello-magic.html
```

```{warning}
Make sure that the app name specified is in the `INSTALLED_APPS` list in your Django settings file (normally `settings.py`).
```

## Use a component

Components usually reside in a regular Django template (unless it is a [direct view](direct-view.md)). The component is "included" (similar to the `include` templatetag) with a `unicorn` templatetag.

```html
<!-- index.html -->
{% load unicorn %}

<!-- The CSRF token is required by Unicorn to prevent cross-site scripting attacks -->
{% csrf_token %}

<!--
Include the `hello-world.html` HTML template with data provided by the `hello_world.HelloWorldView` Python view
-->
{% unicorn 'hello-world' %}
```

## A basic component

An example component consists of the following Python view class and HTML template.

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

`unicorn:model` is the magic that ties the input to the backend component. When this component renders, the input element will include a value of "World" because that is the value of the `name` field in the view. It will read "Hello World" below the input element. When a user types "universe" into the input element, the component is re-rendered with the new `name` -- the text will now be "Hello Universe".

```{note}
By default `unicorn:model` updates are triggered by listening to `input` events on the element. To listen for the `blur` event instead, use the [lazy](templates.md#lazy) modifier.
```

## Pass data to a component

`args` and `kwargs` can be passed into the `unicorn` templatetag from the outer template. They will be available in the component [`component_args`](views.md#component_args) and [`component_kwargs`](views.md#component_kwargs) instance methods respectively.

```html
<!-- index.html -->
{% load unicorn %}
{% csrf_token %}

{% unicorn 'hello-world' "Hello" name="World" %}
```

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    def mount(self):
        arg = self.component_args[0]
        kwarg = self.component_kwargs["name"]

        assert f"{arg} {kwarg}" == "Hello World"
```

Any variable available in the template context can be passed in as an argument.

```html
<!-- index.html -->
{% load unicorn %}
{% csrf_token %}

<!-- Access nested data from the dictionary in the template context and set on the `name` kwarg -->
{% unicorn 'hello-world' name=hello.world.name %}
```

```python
# views.py
from django.shortcuts import render

def index(request):
    context = {"hello": {"world": {"name": "Galaxy"}}}

    return render(request, "index.html", context)
```

The component view which can use the `name` kwarg.

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    def mount(self):
        kwarg = self.component_kwargs["name"]

        assert kwarg == "Galaxy"
```

## Component key

If there are multiple of the same components on the page, a `key` kwarg can be passed into the template. For example, `{% unicorn 'hello-world' key='helloWorldKey' %}`. This is useful when a unique reference to a component is required, but it is optional.

## Component sub-folders

Components can be nested in sub-folders.

```
myapp/
    components/
        __init__.py
        hello/
            __init__.py
            world.py
    templates/
        myapp/
            hello/
                world.html
```

An example of how the above component would be included in a template.

```html
<!-- index.html -->
{% load unicorn %}
{% csrf_token %}

{% unicorn 'hello.world' %}
```
