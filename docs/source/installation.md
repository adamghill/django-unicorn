# Installation

## Prerequisites

`Unicorn` requires a working Django project. If you don't have one yet, follow the [Getting Started](getting-started.md) guide to create a Django project first.

This tutorial assumes you have:
- Python 3.8 or greater installed
- A Django project created and configured
- Basic familiarity with Django apps, views, and templates

## Install `Unicorn`

Install `Unicorn` the same as any other Python package (preferably into a [virtual environment](https://docs.python.org/3/tutorial/venv.html)).

`````{tab-set}

````{tab-item} pip
```sh
python -m pip install django-unicorn
```
````

````{tab-item} poetry
```sh
poetry add django-unicorn
```
````

````{tab-item} pdm
```sh
pdm add django-unicorn
```
````

````{tab-item} rye
```sh
rye add django-unicorn
```
````

````{tab-item} pipenv
```sh
pipenv install django-unicorn
```
````

`````

```{note}
If attempting to install `django-unicorn` and `orjson` is preventing the installation from succeeding, check whether it is using 32-bit Python. Unfortunately, `orjson` is only supported on 64-bit Python. More details in [issue #105](https://github.com/adamghill/django-unicorn/issues/105).
```

## Integrate `Unicorn` with Django

1\. Add `django_unicorn` to the `INSTALLED_APPS` list in the Django settings file (normally `settings.py`).

```python
# settings.py
INSTALLED_APPS = (
    # other apps
    "django_unicorn",  # required for Django to register urls and templatetags
    # other apps
)
```

2\. Add `path("unicorn/", include("django_unicorn.urls")),` into the project's `urls.py`.

```python
# urls.py
urlpatterns = (
    # other urls
    path("unicorn/", include("django_unicorn.urls")),
)
```

3\. Set up your templates with Unicorn template tags.

`Unicorn` requires two template tags in any template that will use components:
- `{% load unicorn %}` - Loads the Unicorn template tags
- `{% unicorn_scripts %}` - Includes the JavaScript needed for Unicorn to work
- `{% csrf_token %}` - Required for security (standard Django requirement)

You can add these to a base template that other templates extend, or to individual templates.

**Option A: Base template (recommended)**

Create or modify your base template (e.g., `templates/base.html`):

```html
<!-- templates/base.html -->
{% load unicorn %}
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}My App{% endblock %}</title>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}
    {% block content %}{% endblock %}
  </body>
</html>
```

Then extend this template in your pages:

```html
<!-- myapp/templates/myapp/index.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Welcome</h1>
  <!-- Your Unicorn components will go here -->
{% endblock %}
```

**Option B: Individual templates**

If you prefer not to use a base template, add the tags to each template that uses Unicorn components:

```html
<!-- myapp/templates/myapp/index.html -->
{% load unicorn %}
<!DOCTYPE html>
<html>
  <head>
    <title>My Page</title>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}
    <h1>Welcome</h1>
    <!-- Your Unicorn components will go here -->
  </body>
</html>
```

## Create your first component

Let's create a complete working example. This section will guide you through creating a simple "Hello World" component.

### 1. Create a Django app (if needed)

If you don't already have a Django app in your project, create one:

```sh
python manage.py startapp myapp
```

Add it to `INSTALLED_APPS` in your `settings.py`:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'myapp',
    'django_unicorn',
]
```

### 2. Create a view and template

Create a view that will render a page containing your Unicorn component:

```python
# myapp/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'myapp/index.html')
```

Create the template directory structure if it doesn't exist, then create the template with Unicorn tags:

```html
<!-- myapp/templates/myapp/index.html -->
{% load unicorn %}
<!DOCTYPE html>
<html>
  <head>
    <title>My First Unicorn Component</title>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}
    <h1>My First Unicorn Component</h1>
    
    <!-- We'll add our component here in step 4 -->
  </body>
</html>
```

### 3. Add a URL pattern

Add a URL pattern for your view. Create `myapp/urls.py` if it doesn't exist:

```python
# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```

Include your app's URLs in the project's main `urls.py`:

```python
# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('unicorn/', include('django_unicorn.urls')),
    path('', include('myapp.urls')),  # Add this line
]
```

### 4. Create a Unicorn component

Now use the `startunicorn` management command to create your first component:

```sh
python manage.py startunicorn myapp hello-world
```

This creates the following files:
```
myapp/
    components/
        __init__.py
        hello_world.py          # Python view class
    templates/
        myapp/
            hello-world.html    # Component template
```

The generated files contain:

```python
# myapp/components/hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    name = "World"
```

```html
<!-- myapp/templates/myapp/hello-world.html -->
<div>
    <input unicorn:model="name" type="text" />
    <br />
    Hello {{ name|title }}!
</div>
```

### 5. Use the component in your template

Add the component to your page template:

```html
<!-- myapp/templates/myapp/index.html -->
{% load unicorn %}
<!DOCTYPE html>
<html>
  <head>
    <title>My First Unicorn Component</title>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}
    <h1>My First Unicorn Component</h1>
    
    {% unicorn 'hello-world' %}
  </body>
</html>
```

### 6. Run the development server

Start your Django development server:

```sh
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser. You should see an input field with "World" in it, and text below saying "Hello World!". When you type in the input field, the text updates automatically - that's Unicorn in action! ✨

### Project structure

After completing these steps, your project structure should look like this:

```
myproject/
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── myapp/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── hello_world.py
│   ├── migrations/
│   ├── models.py
│   ├── templates/
│   │   └── myapp/
│   │       ├── index.html
│   │       └── hello-world.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── manage.py
```

## Next steps

Now that you have a working Unicorn component, you can:
- Learn more about [components](components.md) and their capabilities
- Explore [actions](actions.md) to handle user interactions
- Understand [views](views.md) to add backend logic
- Check out the [example project](https://github.com/adamghill/django-unicorn/tree/main/example) for more complex examples
