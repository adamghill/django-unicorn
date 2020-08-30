# django-unicorn
The magical fullstack framework for Django. ✨

`django-unicorn` provides a way to use backend Django code and regular Django templates to create interactive experiences without investing in a separate frontend framework.

## Why?
Building server-side sites in Django with the ORM and template engine is so pleasant, but once you need more interactivity on the frontend, there is a lot more ambiguity. Should you build out an entire API in Django REST framework? Should you use React or Vue.js (or some) other frontend framework?

It seems like there should be an easier way to create interactive experiences.

## A note
`django-unicorn` is still beta and the API will likely change on the way to version 1.0.0. All efforts will be made to include an easy upgrade path. 1.0.0 will signify that the public API won't change until the next major release.

# Detailed documentation
https://www.django-unicorn.com

# Developing
1. `git clone git@github.com:adamghill/django-unicorn.git`
1. `poetry install`
1. `poetry run example/manage.py migrate`
1. `poetry run example/manage.py runserver 0:8000`
1. Go to `localhost:8000` in your browser
1. To install in another project `pip install -e ../django-unicorn`

## Run unittests
1. `poetry run pytest`

## Minify Javascript
1. `npm install`
1. `npm run-script build`

## Bump version
1. `npm run-script build`
1. `poetry version major|minor|patch`
1. Commit/tag/push version bump
1. `poetry publish --build -r test -u __token__`
1. Make sure test package can be installed as expected (https://test.pypi.org/project/django-unicorn/)
1. `poetry publish -r pypi -u __token__`
1. Make sure live package can be installed as expected (https://pypi.org/project/django-unicorn/)
