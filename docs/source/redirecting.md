# Redirecting

`Unicorn` has a few different ways to redirect from an action method.

## Redirect

To redirect the user, return a `HttpResponseRedirect` from an action method. Using the Django shortcut [`redirect`](https://docs.djangoproject.com/en/stable/topics/http/shortcuts/#redirect) method is one way to do that in a typical Django manner.

```{note}
`django.shortcuts.redirect` can take a Django model, Django view name, an absolute url, or a relative url. However, the `permanent` kwarg for `redirect` has no bearing in this context.
```

```{tip}
It is not required to use `django.shortcuts.redirect`. Anything that returns a `HttpResponseRedirect` will behave the same in `Unicorn`.
```

```python
# redirect.py
from django.shortcuts import redirect
from django_unicorn.components import UnicornView
from .models import Book

class BookView(UnicornView):
    title = ""

    def save_book(self):
        book = Book(title=self.title)
        book.save()
        self.reset()

        return redirect(f"/book/{book.id}")
```

```html
<!-- redirect.html -->
<div>
  <input unicorn:model="title" type="text" id="title" /><br />
  <button unicorn:click="save_book()">Save book</button>
</div>
```

## HashUpdate

To avoid a server-side page refresh and just update the hash at the end of the url, return `HashUpdate` from the action method.

```python
# hash_update.py
from django_unicorn.components import HashUpdate, UnicornView
from .models import Book

class BookView(UnicornView):
    title = ""

    def save_book(self):
        book = Book(title=self.title)
        book.save()
        self.reset()

        return HashUpdate(f"#{book.id}")
```

```html
<!-- hash-update.html -->
<div>
  <input unicorn:model="title" type="text" id="title" /><br />
  <button unicorn:click="save_book()">Save book</button>
</div>
```

## LocationUpdate

To avoid a server-side page refresh and update the whole url, return a `LocationUpdate` from the action method.

`LocationUpdate` is instantiated with a `HttpResponseRedirect` arg and an optional `title` kwarg.

```{note}
`LocationUpdate` uses [`window.history.pushState`](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState) so the new url must be relative or the same origin as the original url.
```

```python
# location_update.py
from django.shortcuts import redirect
from django_unicorn.components import LocationUpdate, UnicornView
from .models import Book

class BookView(UnicornView):
    title = ""

    def save_book(self):
        book = Book(title=self.title)
        book.save()
        self.reset()

        return LocationUpdate(redirect(f"/book/{book.id}"), title=f"{book.title}")
```

```html
<!-- location-update.html -->
<div>
  <input unicorn:model="title" type="text" id="title" /><br />
  <button unicorn:click="save_book()">Save book</button>
</div>
```
