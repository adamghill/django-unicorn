import pytest
import shortuuid
from django.conf import settings
from django.core.cache import caches

from django_unicorn.views.queue import ComponentRequestQueue
from django_unicorn.views.request import ComponentRequest


@pytest.mark.redis
@pytest.mark.django_db
def test_real_redis_queue_behavior(settings):
    # Configure to use real Redis
    settings.UNICORN["SERIAL"]["ENABLED"] = True

    # Force cache reload (important if caches were accessed before settings change)
    if "default" in caches:
        del caches["default"]

    backend_configured = False
    try:
        # Try using Django 4.0+ built-in Redis backend
        import django
        from django.core.cache.backends.redis import RedisCache

        settings.CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/1",
            }
        }
        backend_configured = True
        print(f"Using Django built-in RedisCache (Django {django.get_version()})")
    except ImportError:
        pass

    if not backend_configured:
        try:
            import django_redis

            # Fallback to django-redis
            settings.CACHES = {
                "default": {
                    "BACKEND": "django_redis.cache.RedisCache",
                    "LOCATION": "redis://127.0.0.1:6379/1",
                    "OPTIONS": {
                        "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    },
                }
            }
            print("Using django-redis backend")
        except ImportError:
            pytest.skip("Neither django.core.cache.backends.redis nor django-redis available")

    try:
        import redis

        # Verify connection
        r = redis.from_url("redis://127.0.0.1:6379/1")
        r.ping()
        r.flushdb()  # Clear DB 1 for test safety
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")

    component_id = shortuuid.uuid()[:8]
    queue = ComponentRequestQueue(component_id)

    # Verification: Ensure we are actually using the Redis optimization path
    redis_client = queue._get_redis_client()
    assert redis_client is not None, f"Failed to get Redis client from backend: {queue.cache}"

    # 1. Create a real request
    request = ComponentRequest.__new__(ComponentRequest)
    request.id = component_id
    request.name = "test_redis"
    request.epoch = 100
    request.data = {"count": 1}
    request.action_queue = []
    request.request = None
    request.key = ""
    request.hash = ""

    # 2. Add to queue
    queue.add(request)

    # Verify it is in Redis
    requests = queue.get_all()
    assert len(requests) == 1
    assert requests[0].data == {"count": 1}

    # 3. Modify the request (simulate ActionDispatcher)
    request.data = {"count": 2}

    # 4. Remove from queue using the MODIFIED request object
    queue.remove(request)

    # In Redis path, LREM fails -> item stays in queue.
    # If this assertion fails (len==0), it means we fell back to 'pop(0)' or LREM worked miraculously.
    requests_after_fail = queue.get_all()
    assert len(requests_after_fail) == 1, (
        "Modified request should NOT be removed by Redis LREM (expected behavior requiring fix)"
    )

    # C. Try removing with restored/snapshot object -> Should SUCCEED
    # Restore state (simulating using the snapshot)
    request.data = {"count": 1}
    queue.remove(request)

    requests_final = queue.get_all()
    assert len(requests_final) == 0, "Original/Snapshot request SHOULD be removed"
