import? 'adamghill.justfile'
import? '../dotfiles/just/justfile'

src := "django_unicorn"

# List commands
_default:
    just --list --unsorted --justfile {{ justfile() }} --list-heading $'Available commands:\n'

# Grab default `adamghill.justfile` from GitHub
fetch:
  curl https://raw.githubusercontent.com/adamghill/dotfiles/master/just/justfile > adamghill.justfile

# Run the dev server for the example project
runserver:
    uv run example/manage.py runserver 0:8080

# Run the Python matrix test suite
test-python-matrix:
    act -W .github/workflows/python.yml -j test

# Run the JavaScript unit tests
test-js:
    npm run-script test

# Run both Python and JS tests
test-all:
    test-python-matrix
    test-js

# Build the JavaScript library
js-build:
    npm run build

# Install JS dependencies
js-install:
    npm install

# Run Python unit tests
test-python:
    uv run pytest -m 'not slow'

# Run Python unit tests with benchmarks
test-python-benchmarks:
    uv run pytest tests/benchmarks/ --benchmark-autosave --benchmark-only

# Run Python unit tests with compared benchmarks
test-python-benchmarks-compare:
    uv run pytest tests/benchmarks/ --benchmark-only --benchmark-compare

# Run tests with coverage
test-python-coverage:
    uv run pytest --cov=django_unicorn

type:
    uv run ty check .

# Sphinx autobuild
docs-serve:
    uv run sphinx-autobuild -W docs/source docs/build

# Build documentation
docs-build:
    uv run sphinx-build -W docs/source docs/build

# Build everything (checks, JS, docs)
build:
    type
    test-python
    js-install
    js-build
    docs-build

# Publish package
publish:
    uv build
    uv publish
