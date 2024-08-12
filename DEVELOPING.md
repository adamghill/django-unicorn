# Developing

## Local development

1. Fork https://github.com/adamghill/django-unicorn`
1. `git clone` your forked repository
1. `cd django-unicorn`
1. `poetry install -E minify -E docs`
1. `poetry run python example/manage.py migrate`
1. `poetry run python example/manage.py runserver localhost:8000`
1. Go to `localhost:8000` in your browser

## To install in another project

1. Download the repo to your local
1. `pip install -e ../django-unicorn` from inside the other project's virtualenv _or_ add `django-unicorn = { path="../django-unicorn", develop=true }` to the other project's `pyproject.toml`

## Build Sphinx documentation

1. `poetry run sphinx-autobuild -W docs/source docs/build`

## Run unit tests on local environment

1. Python: `poetry run pytest`
1. JavaScript: `npm run test`

## Run Python/Django matrix unit tests

1. Install [`act`](https://nektosact.com)
1. `act -W .github/workflows/python.yml -j test`

# Minify JavaScript

1. `npm install`
1. `npm run build`

## Bump version

1. Update changelog.md
1. Update package.json
1. `poetry version major|minor|patch`
1. Run all build processes: `poe build`
1. Commit/tag/push version bump
1. `poe publish`
1. Make sure test package can be installed as expected (https://test.pypi.org/project/django-unicorn/)
1. Make sure live package can be installed as expected (https://pypi.org/project/django-unicorn/)
1. [Create GitHub release](https://github.com/adamghill/django-unicorn/releases/new) and add changelog there
1. Update django-unicorn.com's version of `django-unicorn`
