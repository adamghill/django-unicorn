# django-unicorn

![PyPI](https://img.shields.io/pypi/v/django-unicorn?color=blue&style=flat-square)

![GitHub Release Date](https://img.shields.io/github/release-date/adamghill/django-unicorn?style=flat-square)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

The magical fullstack framework for Django. ✨

`Unicorn` is a reactive component framework that progressively enhances a normal Django view, makes AJAX calls in the background, and dynamically updates the DOM. It seamlessly extends Django past its server-side framework roots without giving up all of its niceties or re-building your website.

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

1. `npm run build`
1. `poetry version major|minor|patch`
1. Commit/tag/push version bump
1. `poetry publish --build -r test`
1. Make sure test package can be installed as expected (https://test.pypi.org/project/django-unicorn/)
1. `poetry publish`
1. Make sure live package can be installed as expected (https://pypi.org/project/django-unicorn/)
1. Update django-unicorn.com's changelog.md
1. Update django-unicorn.com's version of `django-unicorn`
1. [Create GitHub release](https://github.com/adamghill/django-unicorn/releases/new) and add changelog there

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://adamghill.com"><img src="https://avatars0.githubusercontent.com/u/317045?v=4" width="100px;" alt=""/><br /><sub><b>Adam Hill</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=adamghill" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=adamghill" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://python3.ninja"><img src="https://avatars1.githubusercontent.com/u/44167?v=4" width="100px;" alt=""/><br /><sub><b>Andres Vargas</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=zodman" title="Code">💻</a></td>
    <td align="center"><a href="http://iskra.ml"><img src="https://avatars3.githubusercontent.com/u/6555851?v=4" width="100px;" alt=""/><br /><sub><b>Eddy Ernesto del Valle Pino</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=edelvalle" title="Code">💻</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/yaser-al-najjar-429b9096/"><img src="https://avatars3.githubusercontent.com/u/10493809?v=4" width="100px;" alt=""/><br /><sub><b>Yaser Al-Najjar</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=yaseralnajjar" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
