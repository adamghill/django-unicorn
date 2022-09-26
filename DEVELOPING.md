# Developing

1. `git clone git@github.com:adamghill/django-unicorn.git`
1. `cd django-unicorn`
1. `poetry install -E minify -E docs`
1. `poetry run python example/manage.py migrate`
1. `poetry run python example/manage.py runserver localhost:8000`
1. Go to `localhost:8000` in your browser

## To install in another project

- `pip install -e ../django-unicorn`
- add something like `django-unicorn = { path="../django-unicorn", develop=true }` to other project's `pyproject.toml`

# See docs

1. `poetry run sphinx-autobuild -W docs/source docs/build`

# Run unittests

1. `poetry run pytest`
1. `npm run test`

# Minify JavaScript

1. `npm install`
1. `npm run build`

# Bump version

1. Run Python tests: `poe t`
1. Run JavaScript tests: `poe tj`
1. Build the JavaScript library: `poe jb`
1. Update changelog.md
1. Build documentation with `poe sb`
1. `poetry version major|minor|patch`
1. Commit/tag/push version bump
1. `poe publish`
1. Make sure test package can be installed as expected (https://test.pypi.org/project/django-unicorn/)
1. Make sure live package can be installed as expected (https://pypi.org/project/django-unicorn/)
1. [Create GitHub release](https://github.com/adamghill/django-unicorn/releases/new) and add changelog there
1. Update django-unicorn.com's version of `django-unicorn`
