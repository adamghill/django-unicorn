# Queue Requests

This is an experimental feature of that queues up slow-processing component views to prevent race conditions. For simple components this should not be necessary.

Serialization is turned off by default, but can be enabled in the [settings](settings.md#serial).

```{warning}
This feature will be disabled automatically if the cache backend is set to ["django.core.cache.backends.dummy.DummyCache"](https://docs.djangoproject.com/en/stable/topics/cache/#dummy-caching-for-development).

[Local memory caching](https://docs.djangoproject.com/en/3.1/topics/cache/#local-memory-caching) (the default if no `CACHES` setting is provided) will work fine if the web server only has one process. For more production use cases, consider using [`redis`](https://github.com/jazzband/django-redis), [`Memcache`](https://docs.djangoproject.com/en/stable/topics/cache/#memcached), or [database caching](https://docs.djangoproject.com/en/stable/topics/cache/#database-caching).
```
