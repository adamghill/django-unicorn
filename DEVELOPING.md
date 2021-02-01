# Developing

1. `git clone git@github.com:adamghill/django-unicorn.git`
1. `poetry install`
1. `poetry run python example/manage.py migrate`
1. `poetry run python example/manage.py runserver localhost:8000`
1. Go to `localhost:8000` in your browser
1. To install in another project `pip install -e ../django-unicorn`

## Run unittests

1. `poetry run pytest`
1. `npm run test`

## Minify Javascript

1. `npm install`
1. `npm run build`

## Bump version

1. `dj t`
1. `npm run build`
1. `poetry version major|minor|patch`
1. Commit/tag/push version bump
1. `poetry publish --build -r test`
1. Make sure test package can be installed as expected (https://test.pypi.org/project/django-unicorn/)
1. `poetry publish`
1. Make sure live package can be installed as expected (https://pypi.org/project/django-unicorn/)
1. [Create GitHub release](https://github.com/adamghill/django-unicorn/releases/new) and add changelog there
1. Update django-unicorn.com's changelog.md
1. Update django-unicorn.com's version of `django-unicorn`
