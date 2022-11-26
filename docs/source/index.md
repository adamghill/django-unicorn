# Introduction

```{toctree}
:maxdepth: 2
:hidden:

self
changelog
faq
```

```{toctree}
:caption: Basics
:maxdepth: 2
:hidden:

installation
components
templates
actions
child-components
django-models
```

```{toctree}
:caption: Features
:maxdepth: 2
:hidden:

direct-view
validation
redirecting
loading-states
dirty-states
partial-updates
polling
visibility
messages
advanced
queue-requests
```

```{toctree}
:caption: Misc
:maxdepth: 2
:hidden:

troubleshooting
settings
cli
architecture
code-of-conduct
PDF <https://www.django-unicorn.com/docs/unicorn-latest.pdf>
GitHub <https://github.com/adamghill/django-unicorn>
Sponsor <https://github.com/sponsors/adamghill>
devmarks.io <https://devmarks.io>
```

`Unicorn` is a reactive component framework that progressively enhances a normal Django view, makes AJAX calls in the background, and dynamically updates the DOM. It seamlessly extends Django past its server-side framework roots without giving up all of its niceties or re-building your website.

```{admonition} Bookmarking for Developers
[devmarks.io](https://devmarks.io) is _Bookmarking for Developers_ -- designed by the creator of Unicorn and [free to try out](https://devmarks.io).
```

## Related projects

`Unicorn` stands on the shoulders of giants, in particular [morphdom](https://github.com/patrick-steele-idem/morphdom) which is integral for merging DOM changes.

### Inspirational projects in other languages

- [Livewire](https://laravel-livewire.com/), a full-stack framework for the PHP web framework, Laravel.
- [LiveView](https://github.com/phoenixframework/phoenix_live_view), a library for the Elixir web framework, Phoenix, that uses websockets.
- [StimulusReflex](https://docs.stimulusreflex.com), a library for the Ruby web framework, Ruby on Rails, that uses websockets.
- [Hotwire](https://hotwire.dev), "is an alternative approach to building modern web applications without using much JavaScript by sending HTML instead of JSON over the wire". Uses AJAX, but can optionally use websockets.

### Full-stack framework Python packages

- [Reactor](https://github.com/edelvalle/reactor/), a port of Elixir's `LiveView` to Django. Especially interesting for more complicated use-cases like chat rooms, keeping multiple browsers in sync, etc. Uses Django channels and websockets to work its magic.
- [Flask-Meld](https://github.com/mikeabrahamsen/Flask-Meld), a port of `Unicorn` to Flask. Uses websockets.
- [Sockpuppet](https://sockpuppet.argpar.se/), a port of Ruby on Rail's `StimulusReflex`. Requires Django channels and websockets.
- [Django inertia.js adapter](https://github.com/zodman/inertia-django) allows Django to use <a href="https://inertiajs.com">inertia.js</a> to build an SPA without building an API.
- [Hotwire for Django](https://github.com/hotwire-django) contains a few different repositiories to integrate [Hotwire](https://hotwire.dev) with Django.
- [Lona](https://lona-web.org/) is a web application framework, designed to write responsive web apps in full Python.
- [IDOM](https://github.com/idom-team/idom), a port of ReactJS to Python. Fully compatible with all ReactJS components.

#### Comparison

| Repo                                                           | Django | Flask | AJAX |   Websockets   |                                           Version                                            | Stars                                                                                                              |
| :------------------------------------------------------------- | :----: | :---: | :--: | :------------: | :------------------------------------------------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------ |
| [Unicorn](https://github.com/adamghill/django-unicorn)         |   ✔    |       |  ✔️  |                |  ![PyPI version](https://img.shields.io/pypi/v/django-unicorn?label=%20&style=flat-square)   | ![GitHub Repo stars](https://img.shields.io/github/stars/adamghill/django-unicorn?label=%20&style=flat-square)     |
| [Reactor](https://github.com/edelvalle/reactor/)               |   ✔️   |       |      |       ✔️       |  ![PyPI version](https://img.shields.io/pypi/v/django-reactor?label=%20&style=flat-square)   | ![GitHub Repo stars](https://img.shields.io/github/stars/edelvalle/reactor?label=%20&style=flat-square)            |
| [Sockpuppet](https://github.com/jonathan-s/django-sockpuppet)  |   ✔️   |       |      |       ✔️       | ![PyPI version](https://img.shields.io/pypi/v/django-sockpuppet?label=%20&style=flat-square) | ![GitHub Repo stars](https://img.shields.io/github/stars/jonathan-s/django-sockpuppet?label=%20&style=flat-square) |
| [Flask-Meld](https://github.com/mikeabrahamsen/Flask-Meld)     |        |  ✔️   |      |       ✔️       |    ![PyPI version](https://img.shields.io/pypi/v/flask-meld?label=%20&style=flat-square)     | ![GitHub Repo stars](https://img.shields.io/github/stars/mikeabrahamsen/Flask-Meld?label=%20&style=flat-square)    |
| [Django IDOM](https://github.com/idom-team/django-idom)        |   ✔️   |       |      |       ✔️       |    ![PyPI version](https://img.shields.io/pypi/v/django-idom?label=%20&style=flat-square)    | ![GitHub Repo stars](https://img.shields.io/github/stars/idom-team/django-idom?label=%20&style=flat-square)        |
| [Turbo Django](https://github.com/hotwire-django/turbo-django) |   ✔️   |       |      | ✔️ for streams |   ![PyPI version](https://img.shields.io/pypi/v/turbo-django?label=%20&style=flat-square)    | ![GitHub Repo stars](https://img.shields.io/github/stars/hotwire-django/turbo-django?label=%20&style=flat-square)  |

### Django component packages

- [django-components](https://github.com/EmilStenstrom/django-components/), which lets you create "template components", that contains both the template, the Javascript and the CSS needed to generate the front end code you need for a modern app.
- [django-component](https://gitlab.com/Mojeer/django_components), which provides declarative and composable components for Django, inspired by JavaScript frameworks.
- [django-page-components](https://github.com/andreyfedoseev/django-page-components), a minimalistic framework for creating page components and using them in your Django views and templates.
- [slippers](https://mitchel.me/slippers/), helps build reusable components in Django without writing a single line of Python.
- [django_slots](https://github.com/nwjlyons/django_slots) allows multiline strings to be captured and passed to template tags.

### Django packages to integrate lightweight frontend frameworks

- [django-htmx](https://github.com/adamchainz/django-htmx) which has extensions for using Django with [htmx](https://htmx.org/).
