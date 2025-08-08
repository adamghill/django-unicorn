<p align="center">
  <a href="https://www.django-unicorn.com/"><img src="https://github.com/adamghill/django-unicorn/raw/a98539b6e4b1123705559116a77e63eea7e2b8d0/img/unicorn-logo.png" alt="django-unicorn logo" height="200"/></a>
</p>

<h1 align="center">
  <a href="https://www.django-unicorn.com/">Unicorn</a>
  <p>The magical reactive component framework for Django ✨</p>
</h1>

![PyPI](https://img.shields.io/pypi/v/django-unicorn?color=blue&style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/django-unicorn?color=blue&style=flat-square)
![coverage](https://raw.githubusercontent.com/adamghill/django-unicorn/python-coverage-comment-action-data/badge.svg)
![GitHub Sponsors](https://img.shields.io/github/sponsors/adamghill?color=blue&style=flat-square)
[![All Contributors](https://img.shields.io/badge/all_contributors-17-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE - Do not remove or modify above line -->

[Unicorn](https://www.django-unicorn.com) adds modern reactive component functionality to your Django templates without having to learn a new templating language or fight with complicated JavaScript frameworks. It seamlessly extends Django past its server-side framework roots without giving up all of its niceties or forcing you to rebuild your application. With Django Unicorn, you can quickly and easily add rich front-end interactions to your templates, all while using the power of Django.

**[https://www.django-unicorn.com](https://www.django-unicorn.com) has extensive documentation, code examples, and more!**

## ⚡ Getting started

### 1. [Install the package](https://www.django-unicorn.com/docs/installation/)

`pip install django-unicorn` OR `poetry add django-unicorn`

### 2. Add `django_unicorn` to `INSTALLED_APPS`

```python
# settings.py
INSTALLED_APPS = (
    # other apps
    "django_unicorn",
)
```

### 3. Update urls.py

```python
# urls.py
import django_unicorn

urlpatterns = (
    # other urls
    path("unicorn/", include("django_unicorn.urls")),
)
```

### 4. Add `Unicorn` to the HTML template

```html
<!-- template.html -->
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

### 5. [Create a component](https://www.django-unicorn.com/docs/components/)

`python manage.py startunicorn myapp COMPONENT_NAME`

`Unicorn` uses the term "component" to refer to a set of interactive functionality that can be put into templates. A component consists of a Django HTML template and a Python view class which contains the backend code. After running the management command, two new files will be created:

- `myapp/templates/unicorn/COMPONENT_NAME.html` (component template)
- `myapp/components/COMPONENT_NAME.py` (component view)

### 6. Add the component to your template

```html
<!-- template.html -->
{% load unicorn %}

<html>
  <head>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}

    {% unicorn 'COMPONENT_NAME' %}
  </body>
</html>
```

## [Example todo component](https://www.django-unicorn.com/examples/todo)

The `unicorn:` attributes bind the element to data and can also trigger methods by listening for events, e.g. `click`, `input`, `keydown`, etc.

```html
<!-- todo.html -->

<div>
  <form unicorn:submit.prevent="add">
    <input type="text"
      unicorn:model.defer="task"
      unicorn:keyup.escape="task=''"
      placeholder="New task" id="task"></input>
  </form>
  <button unicorn:click="add">Add</button>
  <button unicorn:click="$reset">Clear all tasks</button>

  <p>
    {% if tasks %}
      <ul>
        {% for task in tasks %}
          <li>{{ task }}</li>
        {% endfor %}
      </ul>
    {% else %}
      No tasks 🎉
    {% endif %}
  </p>
</div>
```

```python
# todo.py

from django_unicorn.components import UnicornView
from django import forms

class TodoForm(forms.Form):
    task = forms.CharField(min_length=2, max_length=20, required=True)

class TodoView(UnicornView):
    form_class = TodoForm

    task = ""
    tasks = []

    def add(self):
        if self.is_valid():
            self.tasks.append(self.task)
            self.task = ""
```

## ✨ Wait, is this magic?

Sort of! At least it might feel like it. 🤩

1. `Unicorn` progressively enhances a normal Django view, so the initial render is fast and great for SEO.
2. `Unicorn` binds to the elements you specify and automatically makes AJAX calls when needed.
3. `Unicorn` seamlessly updates the DOM when the HTML changes.

Focus on building regular Django templates and Python classes without needing to switch to another language or use unnecessary infrastructure.

## 🤯 But wait, there's more!

As if that wasn't enough, other features include:

- [Form Validation](https://www.django-unicorn.com/docs/validation/)
- [Redirection](https://www.django-unicorn.com/docs/redirecting/)
- [Loading States](https://www.django-unicorn.com/docs/loading-states/)
- [Dirty States](https://www.django-unicorn.com/docs/dirty-states/)
- [Partial Updates](https://www.django-unicorn.com/docs/partial-updates/)
- [Polling](https://www.django-unicorn.com/docs/polling/)
- [Scroll Triggering](https://www.django-unicorn.com/docs/visibility/)
- [Messages](https://www.django-unicorn.com/docs/messages/)
- [Javascript Integration](https://www.django-unicorn.com/docs/advanced/)

## 📖 Dig In

- [Documentation](https://www.django-unicorn.com/docs/)
- [Examples](https://www.django-unicorn.com/examples/todo)
- [Screencasts](https://www.django-unicorn.com/screencasts/installation)
- [Changelog](https://www.django-unicorn.com/docs/changelog/)

## ❤️ Support

This project is supported by GitHub [Sponsors](https://github.com/sponsors/adamghill) and [Digital Ocean](https://m.do.co/c/617d629f56c0).

<p>
  <a href="https://m.do.co/c/617d629f56c0">
    <img src="https://opensource.nyc3.cdn.digitaloceanspaces.com/attribution/assets/SVG/DO_Logo_horizontal_blue.svg" width="201px">
  </a>
</p>

## 🔧 Contributors

Check out [this guide](DEVELOPING.md) for more details on how to contribute.

Thanks to the following wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)) who have helped build `Unicorn`.

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://adamghill.com"><img src="https://avatars0.githubusercontent.com/u/317045?v=4?s=100" width="100px;" alt="Adam Hill"/><br /><sub><b>Adam Hill</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=adamghill" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=adamghill" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://python3.ninja"><img src="https://avatars1.githubusercontent.com/u/44167?v=4?s=100" width="100px;" alt="Andres Vargas"/><br /><sub><b>Andres Vargas</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=zodman" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://iskra.ml"><img src="https://avatars3.githubusercontent.com/u/6555851?v=4?s=100" width="100px;" alt="Eddy Ernesto del Valle Pino"/><br /><sub><b>Eddy Ernesto del Valle Pino</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=edelvalle" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.linkedin.com/in/yaser-al-najjar-429b9096/"><img src="https://avatars3.githubusercontent.com/u/10493809?v=4?s=100" width="100px;" alt="Yaser Al-Najjar"/><br /><sub><b>Yaser Al-Najjar</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=yaseralnajjar" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sbidy"><img src="https://avatars.githubusercontent.com/u/1077364?v=4?s=100" width="100px;" alt="Stephan Traub"/><br /><sub><b>Stephan Traub</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=sbidy" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/frbor"><img src="https://avatars.githubusercontent.com/u/2320183?v=4?s=100" width="100px;" alt="Fredrik Borg"/><br /><sub><b>Fredrik Borg</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=frbor" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=frbor" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/mbacicc"><img src="https://avatars.githubusercontent.com/u/46646960?v=4?s=100" width="100px;" alt="mbacicc"/><br /><sub><b>mbacicc</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=mbacicc" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://ambient-innovation.com"><img src="https://avatars.githubusercontent.com/u/3176075?v=4?s=100" width="100px;" alt="Ron"/><br /><sub><b>Ron</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=GitRon" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Franziskhan"><img src="https://avatars.githubusercontent.com/u/86062014?v=4?s=100" width="100px;" alt="Franziskhan"/><br /><sub><b>Franziskhan</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=Franziskhan" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/joshiggins"><img src="https://avatars.githubusercontent.com/u/5124298?v=4?s=100" width="100px;" alt="Josh Higgins"/><br /><sub><b>Josh Higgins</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=joshiggins" title="Tests">⚠️</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=joshiggins" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/MayasMess"><img src="https://avatars.githubusercontent.com/u/51958712?v=4?s=100" width="100px;" alt="Amayas Messara"/><br /><sub><b>Amayas Messara</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=MayasMess" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.apoorvapandey.com"><img src="https://avatars.githubusercontent.com/u/21103831?v=4?s=100" width="100px;" alt="Apoorva Pandey"/><br /><sub><b>Apoorva Pandey</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=apoorvaeternity" title="Tests">⚠️</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=apoorvaeternity" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://www.nerdocs.at"><img src="https://avatars.githubusercontent.com/u/2955584?v=4?s=100" width="100px;" alt="Christian González"/><br /><sub><b>Christian González</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=nerdoc" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=nerdoc" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/robwa"><img src="https://avatars.githubusercontent.com/u/4658937?v=4?s=100" width="100px;" alt="robwa"/><br /><sub><b>robwa</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=robwa" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=robwa" title="Tests">⚠️</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://medium.com/@pbadeer"><img src="https://avatars.githubusercontent.com/u/467756?v=4?s=100" width="100px;" alt="Preston Badeer"/><br /><sub><b>Preston Badeer</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=pbadeer" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/stat1c-void"><img src="https://avatars.githubusercontent.com/u/9142081?v=4?s=100" width="100px;" alt="Sergei"/><br /><sub><b>Sergei</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=stat1c-void" title="Documentation">📖</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=stat1c-void" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=stat1c-void" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/bazubii"><img src="https://avatars.githubusercontent.com/u/12039914?v=4?s=100" width="100px;" alt="bazubii"/><br /><sub><b>bazubii</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=bazubii" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=bazubii" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/dancaron"><img src="https://avatars.githubusercontent.com/u/535851?v=4?s=100" width="100px;" alt="Dan Caron"/><br /><sub><b>Dan Caron</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=dancaron" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://hauntsaninja.github.io/"><img src="https://avatars.githubusercontent.com/u/12621235?v=4?s=100" width="100px;" alt="Shantanu"/><br /><sub><b>Shantanu</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=hauntsaninja" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/regoawt"><img src="https://avatars.githubusercontent.com/u/49868464?v=4?s=100" width="100px;" alt="regoawt"/><br /><sub><b>regoawt</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=regoawt" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=regoawt" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/lassebomh"><img src="https://avatars.githubusercontent.com/u/31809070?v=4?s=100" width="100px;" alt="Lasse H. Bomholt"/><br /><sub><b>Lasse H. Bomholt</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=lassebomh" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://marteydodoo.com"><img src="https://avatars.githubusercontent.com/u/49076?v=4?s=100" width="100px;" alt="Martey Dodoo"/><br /><sub><b>Martey Dodoo</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=martey" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://digitalpinup.art"><img src="https://avatars.githubusercontent.com/u/1392097?v=4?s=100" width="100px;" alt="Pierre"/><br /><sub><b>Pierre</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=bloodywing" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://roman.pt"><img src="https://avatars.githubusercontent.com/u/75075?v=4?s=100" width="100px;" alt="Roman Imankulov"/><br /><sub><b>Roman Imankulov</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=imankulov" title="Tests">⚠️</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=imankulov" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/rhymiz"><img src="https://avatars.githubusercontent.com/u/7029352?v=4?s=100" width="100px;" alt="Lemi Boyce"/><br /><sub><b>Lemi Boyce</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=rhymiz" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://jacksund.github.io"><img src="https://avatars.githubusercontent.com/u/47992949?v=4?s=100" width="100px;" alt="Jack Sundberg"/><br /><sub><b>Jack Sundberg</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=jacksund" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/siliconcow"><img src="https://avatars.githubusercontent.com/u/908362?v=4?s=100" width="100px;" alt="siliconcow"/><br /><sub><b>siliconcow</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=siliconcow" title="Code">💻</a> <a href="https://github.com/adamghill/django-unicorn/commits?author=siliconcow" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://rahma.hashnode.dev/"><img src="https://avatars.githubusercontent.com/u/35562131?v=4?s=100" width="100px;" alt="Akintola Rahmat"/><br /><sub><b>Akintola Rahmat</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=mihrab34" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://www.pythonbynight.com"><img src="https://avatars.githubusercontent.com/u/46942991?v=4?s=100" width="100px;" alt="Mario Munoz"/><br /><sub><b>Mario Munoz</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=tataraba" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/epw1624"><img src="https://avatars.githubusercontent.com/u/112768709?v=4?s=100" width="100px;" alt="Emily Wood"/><br /><sub><b>Emily Wood</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=epw1624" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://quiescent.us"><img src="https://avatars.githubusercontent.com/u/2302957?v=4?s=100" width="100px;" alt="Jeremy Wright"/><br /><sub><b>Jeremy Wright</b></sub></a><br /><a href="https://github.com/adamghill/django-unicorn/commits?author=JeremyLWright" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
