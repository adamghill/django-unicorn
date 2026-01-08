# Developing

## Local development

1. Fork https://github.com/adamghill/django-unicorn`
1. `git clone` your forked repository
1. `cd django-unicorn`
1. `uv sync --extra minify --extra docs`
1. `just runserver`
1. Go to `localhost:8080` in your browser

## To install in another project

1. Download the repo to your local
1. `pip install -e ../django-unicorn` from inside the other project's virtualenv _or_ add `django-unicorn = { path="../django-unicorn", develop=true }` to the other project's `pyproject.toml`

## Build Sphinx documentation

1. `just docs-serve`

## Run unit tests on local environment

1. Python: `just test-python`
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
1. Update version in `pyproject.toml`
1. Run all build processes: `just build`
1. Commit/tag/push version bump
1. `just publish`
1. Make sure test package can be installed as expected (https://test.pypi.org/project/django-unicorn/)
1. Make sure live package can be installed as expected (https://pypi.org/project/django-unicorn/)
1. [Create GitHub release](https://github.com/adamghill/django-unicorn/releases/new) and add changelog there
1. Update django-unicorn.com's version of `django-unicorn`
