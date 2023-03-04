<p align="center">
  <a href="https://www.django-unicorn.com/"><img src="img/gu-logo.png" alt="django-unicorn logo" height="200"/></a>
</p>

# Django Unicorn
✨ The Magical Full-Stack Framework for Django ✨

![PyPI](https://img.shields.io/pypi/v/django-unicorn?color=blue&style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/django-unicorn?color=blue&style=flat-square)
![GitHub Sponsors](https://img.shields.io/github/sponsors/adamghill?color=blue&style=flat-square)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-17-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[Django Unicorn](https://www.django-unicorn.com) allows you to quickly add modern site functionality to your Django templates without having to learn a new templating language or fight with complicated JavaScript frameworks. Unicorn is a reactive component framework that progressively enhances a normal Django view, makes AJAX calls in the background, and dynamically updates the DOM. It seamlessly extends Django past its server-side framework roots without giving up all of its niceties or forcing you to re-building your application. With Django Unicorn, you can quickly and easily add rich interactions to your templates, all while using the power of Django.


## ⚡ Getting Started

1. Install the package.
```pip install django-unicorn```

2. Add `django_unicorn` to INSTALLED_APPS.

```
<!-- settings.py -->
INSTALLED_APPS = (
    ...
    "django_unicorn",
)
```

3. Update urls.py to allow the magic to flow.

```
<!-- urls.py -->
urlpatterns = (
    # other urls
    path("unicorn/", include("django_unicorn.urls")),
)
```

4. Add `{% load unicorn %}` to the top of your template.

5. Add `{% unicorn_scripts %}` into your template and make sure there is a `{% csrf_token %}` in there as well.

```
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


6. Create a component from the command line.
```python manage.py startunicorn todo```


7. Check out this Wizardry.

```
<!-- unicorn/templates/unicorn/todo.html -->
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

```
# unicorn/components/todo.py
from django_unicorn.components import UnicornView
from django import forms

class TodoForm(forms.Form):
    task = forms.CharField(min_length=2, max_length=20, required=True)

class TodoView(UnicornView):
    task = ""
    tasks = []

    def add(self):
        if self.is_valid():
            self.tasks.append(self.task)
            self.task = ""
```

8. Add the component to any template with `{% unicorn 'todo' %}`

9. Forget about complicated front-end frameworks.

## 📖 Learn More

- [Changelog](https://www.django-unicorn.com/docs/changelog/)
- [Docs](https://www.django-unicorn.com/docs/)
- [Screencasts](https://www.django-unicorn.com/screencasts/installation)
- [Examples](https://www.django-unicorn.com/examples/todo)

## 🔧 Contributors

### Python

1. `poetry install -E minify -E docs`
1. `poetry run pytest`

### JavaScript

1. `npm install`
1. `npm run test`

Check out [DEVELOPING.md](DEVELOPING.md) for more details.

## 👏 Contributors

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

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
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
