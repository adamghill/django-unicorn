# FAQ

## Do I need to learn a new frontend framework for `Unicorn`?

Nope! `Unicorn` gives you some magical template tags and HTML attributes to sprinkle in normal Django HTML templates. The backend code is a simple class that ultimately derives from `TemplateView`. Keep using the same Django HTML templates, template tags, filters, etc and the best-in-class Django ORM without learning another new framework of the week.

## Do I need to build an entire API to use `Unicorn`?

Nope! `Django REST framework` is pretty magical on its own, and if you will need a mobile app or other use for a REST API, it's a great set of abstractions to follow REST best practices. But, it can be challenging implementing a robust API even with `Django REST framework`. And I wouldn't even attempt to build an API up from scratch unless it was extremely limited.

## Do I need to install GraphQL to use `Unicorn`?

Nope! GraphQL is an awesome piece of technology for specific use-cases and solves some pain points around creating a RESTful API, but it is another thing to wrestle with.

## Do I need to run an annoying separate node.js process or learn any tedious Webpack configuration incantations to use `Unicorn`?

Nope! `Unicorn` [installs](installation.md) just like any normal Django package and is seamless to implement. There <em>are</em> a few "magic" attributes to sprinkle into a Django HTML template, but other than that it's just like building a regular server-side application.

## Does this replace Vue.js or React?

Nope! In some cases, you might need to actually build an {abbr}`SPA (Single Page Application)` in which case `Unicorn` really isn't that helpful. In that case you might have to invest the time to learn a more involved frontend framework. Read [Using VueJS alongside Django](https://tkainrad.dev/posts/use-vuejs-with-django/) for one approach, or check out [other articles](https://www.django-unicorn.com/articles) about this.

## Isn't calling an AJAX endpoint on every input slow?

Not really! `Unicorn` is ideal for when an AJAX call would already be required (such as hitting an API for typeahead search or update data in a database). If that isn't required, the [lazy](templates.md#lazy) and [debounce](templates.md#debounce) modifiers can also be used to prevent an AJAX call on every change.

## But, what about security?

`Unicorn` follows the best practices of Django and requires a [CSRF token](https://docs.djangoproject.com/en/stable/ref/csrf/#how-it-works) to be set on any page that has a component. This ensures that no nefarious AJAX POSTs can be executed. `Unicorn` also creates a unique component checksum with the Django [secret key](https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY) on every data change which also ensures that all updates are valid.

## What browsers does `Unicorn` support?

`Unicorn` mostly targets modern browsers, but any PRs to help support legacy browsers would be appreciated.

## How to make sure that the new JavaScript is served when a new version of `Unicorn` is released?

`Unicorn` works great using [whitenoise](https://whitenoise.evans.io/en/stable/) to serve static assets with a filename based on a hash of the file. [CompressedManifestStaticFilesStorage](http://whitenoise.evans.io/en/stable/django.html#add-compression-and-caching-support) works great for this purpose and is used by [django-unicorn.com](https://www.django-unicorn.com/) for this very purpose. Example code can be found at [https://github.com/adamghill/django-unicorn.com/](https://github.com/adamghill/django-unicorn.com/blob/cb79932/project/settings.py#L72).

## What is the difference between `Unicorn` and lighter front-end frameworks like `htmx` or `alpine.js`?

[htmx](https://htmx.org/) and [alpine.js](https://github.com/alpinejs/alpine) are great libraries to provide interactivity to your HTML. Both of those libraries are generalized front-end framework that you could use with any server-side framework (or just regular HTML). They are both well-supported, battle-tested, and answers to how they work are probably Google-able (or on [Stackoverflow](https://stackoverflow.com/questions/tagged/alpine.js)).

`Unicorn` isn't in the same league as either `htmx` or `alpine.js`. But, the benefit of `Unicorn` is that it is tightly integrated with Django and it should "feel" like an extension of the core Django experience. For example:

- [redirecting](redirecting.md) from an action uses the Django `redirect` shortcut
- [validation](validation.md) uses Django forms
- [Django Models](django-models.md) are tightly integrated
- [Django messages](messages.md) "just work" the way you would expect them to
- you won't have to create extra URLs/views for AJAX calls to send back HTML because `Unicorn` handles all of that for you
