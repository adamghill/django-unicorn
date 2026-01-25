from unittest.mock import patch

import pytest
import shortuuid
from django.conf import settings

from django_unicorn.views.queue import ComponentRequestQueue
from tests.views.message.utils import post_and_get_response


class MockRedis:
    def __init__(self):
        self.store = {}

    def rpush(self, key, value):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append(value)

    def lrange(self, key, start, end):
        # Simplistic slice handling for 0, -1
        if key not in self.store:
            return []
        if end == -1:
            return self.store[key][start:]
        return self.store[key][start : end + 1]

    def lrem(self, key, _, value):
        if key not in self.store:
            return 0
        try:
            self.store[key].remove(value)
            return 1
        except ValueError:
            return 0

    def delete(self, key):
        if key in self.store:
            del self.store[key]

    def expire(self, key, timeout):
        pass


@pytest.mark.benchmark(group="serial_overhead")
def test_benchmark_serial_disabled(benchmark, client):
    settings.UNICORN["SERIAL"]["ENABLED"] = False

    def run_request():
        post_and_get_response(
            client,
            url="/message/tests.views.fake_components.FakeComponent",
            data={"method_count": 0},
            action_queue=[
                {
                    "payload": {"name": "test_method"},
                    "type": "callMethod",
                }
            ],
            component_id=shortuuid.uuid()[:8],
        )

    benchmark(run_request)


@pytest.mark.benchmark(group="serial_overhead")
def test_benchmark_serial_enabled_fallback(benchmark, client):
    settings.UNICORN["SERIAL"]["ENABLED"] = True

    # Ensure no redis client is returned (fallback path)
    with patch.object(ComponentRequestQueue, "_get_redis_client", return_value=None):

        def run_request():
            post_and_get_response(
                client,
                url="/message/tests.views.fake_components.FakeComponent",
                data={"method_count": 0},
                action_queue=[
                    {
                        "payload": {"name": "test_method"},
                        "type": "callMethod",
                    }
                ],
                component_id=shortuuid.uuid()[:8],
            )

        benchmark(run_request)


@pytest.mark.benchmark(group="serial_overhead")
def test_benchmark_serial_enabled_redis_mock(benchmark, client):
    settings.UNICORN["SERIAL"]["ENABLED"] = True

    mock_redis = MockRedis()

    with patch.object(ComponentRequestQueue, "_get_redis_client", return_value=mock_redis):

        def run_request():
            post_and_get_response(
                client,
                url="/message/tests.views.fake_components.FakeComponent",
                data={"method_count": 0},
                action_queue=[
                    {
                        "payload": {"name": "test_method"},
                        "type": "callMethod",
                    }
                ],
                component_id=shortuuid.uuid()[:8],
            )

        benchmark(run_request)


@pytest.mark.benchmark(group="serial_overhead")
def test_benchmark_serial_enabled_redis_real(benchmark, client, settings):
    try:
        import django_redis  # noqa: F401, PLC0415
        import redis  # noqa: PLC0415

        # Test connection
        r = redis.Redis(host="127.0.0.1", port=6379, db=1)
        r.ping()
        r.close()
    except Exception:
        pytest.skip("Redis not available or django-redis not installed")

    settings.UNICORN["SERIAL"]["ENABLED"] = True
    settings.CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

    # Ensure queue uses the new cache
    # Since ComponentRequestQueue initializes cache in __init__, it should pick up the new settings
    # if we create new requests.
    # But `caches` object in `django.core.cache` creates backends on access.
    # `post_and_get_response` triggers view which initializes `ComponentRequestQueue`.

    def run_request():
        post_and_get_response(
            client,
            url="/message/tests.views.fake_components.FakeComponent",
            data={"method_count": 0},
            action_queue=[
                {
                    "payload": {"name": "test_method"},
                    "type": "callMethod",
                }
            ],
            component_id=shortuuid.uuid()[:8],
        )

    benchmark(run_request)
