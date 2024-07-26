# Installation

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

2\. Add `path("unicorn/", include("django_unicorn.urls")),`into the project's`urls.py`.

```python
# urls.py
urlpatterns = (
    # other urls
    path("unicorn/", include("django_unicorn.urls")),
)
```

3\. Add `{% load unicorn %}` to the top of the Django HTML template.

```{note}
Generally, your Django HTML templates are typically created in the `myapp/templates/myapp` directory. You will need to add `{% load unicorn %}` at the top of each of the templates utilizing a `Unicorn` component. Alternatively, you can create one "base" template that is extended by other templates, in which case, you would only need to add `{% load unicorn %}` to the top of your base template.
```

4\. Add `{% unicorn_scripts %}` into the Django HTML template and make sure there is a `{% csrf_token %}` in the template as well.

```html
<!-- index.html -->
{% load unicorn %}
<html>
  <head>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}
  </body>
</html>
```

Then, [create a component](components.md).
