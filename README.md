# django-unicorn
The magical fullstack framework for Django. ✨

# Install
1. `pip install django-unicorn`
1. `python manage.py startunicorn hello-world`
1. Add `django-unicorn` and `unicorn` to `INSTALL_APPS` in your Django settings file
1. Add `path("unicorn/", include("django_unicorn.urls")),` into your project's `urlpatterns` in `urls.py`
1. Add `{% load unicorn %}` to the top of your base template file
1. Add `{% unicorn_styles %}` and `{% unicorn_scripts %}` into your base HTML file

# Current functionality
- `unicorn_styles`, `unicorn_scripts`, `unicorn` template tags
- Base `component` class
- Handles text input, checkbox, select options, select multiple options

# Developing
1. `git clone git@github.com:adamghill/django-unicorn.git`
1. `poetry install`
1. `poetry run example/manage.py migrate`
1. `poetry run example/manage.py runserver 0:8000`
1. Go to `localhost:8000` in your browser
1. To install in another project `pip install -e some_folder/django-unicorn` and follow install instructions above
