import contextlib
import logging
import pickle
import time
from typing import Any

from django.core.cache import caches

from django_unicorn.settings import get_cache_alias, get_serial_timeout
from django_unicorn.views.request import ComponentRequest

logger = logging.getLogger(__name__)


LOCK_TIMEOUT = 2


class ComponentRequestQueue:
    def __init__(self, component_id: str):
        self.cache_key = f"unicorn:queue:{component_id}"
        self.lock_key = f"{self.cache_key}:lock"
        self.cache = caches[get_cache_alias()]
        self.timeout = get_serial_timeout()

    def _get_redis_client(self) -> Any | None:
        # django-redis
        if hasattr(self.cache, "client") and hasattr(self.cache.client, "get_client"):
            with contextlib.suppress(Exception):
                return self.cache.client.get_client()

        # Django 4+ RedisCache or other backends exposing client
        if hasattr(self.cache, "get_client"):
            with contextlib.suppress(Exception):
                # Some implementations require arguments or work differently, so we wrap in try/except
                return self.cache.get_client()

        # Django 4+ RedisCache (django.core.cache.backends.redis.RedisCache)
        if hasattr(self.cache, "_cache") and hasattr(self.cache._cache, "get_client"):
            with contextlib.suppress(Exception):
                return self.cache._cache.get_client()

        # Fallback inspection for `_client` (private but common in some wrappers)
        if hasattr(self.cache, "_client"):
            return self.cache._client

        return None

    @contextlib.contextmanager
    def _lock(self):
        # Use backend specific lock if available (e.g. Redis)
        if hasattr(self.cache, "lock"):
            with contextlib.suppress(Exception):
                with self.cache.lock(self.lock_key, timeout=2):
                    yield
                return

        # Generic spin-lock implementation using cache.add
        acquired = False
        start_time = time.time()

        try:
            while not acquired:
                acquired = self.cache.add(self.lock_key, 1, timeout=LOCK_TIMEOUT)
                if acquired:
                    break

                if time.time() - start_time > LOCK_TIMEOUT:
                    logger.warning(f"Could not acquire lock for {self.cache_key} after {LOCK_TIMEOUT} seconds.")
                    break

                time.sleep(0.005)

            yield
        finally:
            if acquired:
                self.cache.delete(self.lock_key)

    def add(self, request: ComponentRequest):
        # Remove request object to allow pickling
        request.request = None

        client = self._get_redis_client()
        if client:
            try:
                # Use Redis List operations (Atomic)
                # RPUSH adds to tail
                pickled_request = pickle.dumps(request)
                client.rpush(self.cache_key, pickled_request)
                # Set expiry if needed.
                # Ideally we set expiry on every push or check ttl?
                # A queue should probably expire if untouched.
                client.expire(self.cache_key, self.timeout)
                return
            except Exception as e:
                logger.warning(f"Redis optimization failed, falling back to lock: {e}")

        with self._lock():
            requests = self._get_all()
            requests.append(request)
            self._set_all(requests)

    def get_all(self) -> list[ComponentRequest]:
        client = self._get_redis_client()
        if client:
            try:
                # LRANGE 0 -1 gets all elements
                # Note: This does not clear the queue, just reads it.
                raw_items = client.lrange(self.cache_key, 0, -1)
                return [pickle.loads(item) for item in raw_items]  # noqa: S301
            except Exception as e:
                logger.warning(f"Redis optimization failed, falling back to standard get: {e}")

        return self._get_all()

    def _get_all(self) -> list[ComponentRequest]:
        return self.cache.get(self.cache_key) or []

    def _set_all(self, requests: list[ComponentRequest]):
        self.cache.set(self.cache_key, requests, timeout=self.timeout)

    def remove(self, request: ComponentRequest):
        # Remove request object properties to ensure match with stored version?
        # The stored version had request=None and was pickled.
        # Ensure input request has request=None?
        request.request = None

        client = self._get_redis_client()
        if client:
            try:
                # LREM key count value
                # count=1 means remove 1st occurrence from head?
                # count=0 means remove all occurrences.
                # count=-1 means remove from tail.
                # We probably want to remove 1 occurrence.
                pickled_request = pickle.dumps(request)
                removed_count = client.lrem(self.cache_key, 1, pickled_request)

                if removed_count == 0:
                    logger.warning(f"Could not find processed request in queue (Redis LREM): {request}")
                    pass

                return
            except Exception as e:
                logger.warning(f"Redis optimization failed, falling back to lock: {e}")

        with self._lock():
            requests = self._get_all()
            if request in requests:
                requests.remove(request)
                self._set_all(requests)
            else:
                logger.warning(f"Could not find processed request in queue: {request} -- {requests}")
                # Fallback for safety
                if requests:
                    requests.pop(0)
                    self._set_all(requests)

    def clean(self):
        client = self._get_redis_client()
        if client:
            with contextlib.suppress(Exception):
                client.delete(self.cache_key)
                return

        with self._lock():
            self.cache.delete(self.cache_key)


class RequestMerger:
    @staticmethod
    def merge(first: ComponentRequest, others: list[ComponentRequest]) -> ComponentRequest:
        """
        Merges a list of requests into a single request, primarily combining action queues.
        """
        if not others:
            return first

        merged_request = others[0]

        for i in range(1, len(others)):
            other = others[i]
            merged_request.action_queue.extend(other.action_queue)

        return merged_request
