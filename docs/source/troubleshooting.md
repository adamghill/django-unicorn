# Troubleshooting

## Disallowed MIME type error on Windows

Apparently Windows system-wide MIME type configuration sometimes won't load up JavaScript modules in certain browsers. The errors would be something like `Loading module from “http://127.0.0.1:8000/static/js/unicorn.js” was blocked because of a disallowed MIME type (“text/plain”)` or `Failed to load module script: The server responded with a non-JavaScript MIME type of "text/plain".`

One suggested solution is to add the following to the bottom of the settings file:

```python
# settings.py

if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
```

See this [Windows MIME type detection pitfalls](https://www.taricorp.net/2020/windows-mime-pitfalls/) article, this [StackOverflow answer](https://stackoverflow.com/a/16355034), or [issue #201](https://github.com/adamghill/django-unicorn/issues/201) for more details.

## Missing CSRF token or 403 Forbidden errors

`Unicorn` uses CSRF to protect its endpoint from malicious actors. The two parts that are required for CSRF are `"django.middleware.csrf.CsrfViewMiddleware"` in `MIDDLEWARE` and `{% csrf_token %}` in the template that includes any `Unicorn` components.

```python
# settings.py

...
MIDDLEWARE = [
    ...
    "django.middleware.csrf.CsrfViewMiddleware",
    ...
]
```

```html
<!-- template.html -->
{% load unicorn %}

<html>
  <head>
    {% unicorn_scripts %}
  </head>
  <body>
    {% csrf_token %}

    {% unicorn 'hello-world' %}
  </body>
</html>
```
