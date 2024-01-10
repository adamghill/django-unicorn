import logging
import pickle
from typing import List

from django.core.cache import caches
from django.http import HttpRequest

import django_unicorn
from django_unicorn.errors import UnicornCacheError
from django_unicorn.settings import get_cache_alias

logger = logging.getLogger(__name__)


class PointerUnicornView:
    def __init__(self, component_cache_key):
        self.component_cache_key = component_cache_key
        self.parent = None
        self.children = []


class CacheableComponent:
    """
    Updates a component into something that is cacheable/pickleable. Also set pointers to parents/children.
    Use in a `with` statement or explicitly call `__enter__` `__exit__` to use. It will restore the original component
    on exit.
    """

    def __init__(self, component: "django_unicorn.views.UnicornView"):
        self._state = {}
        self.cacheable_component = component

    def __enter__(self):
        components = []
        components.append(self.cacheable_component)

        while components:
            component = components.pop()

            if component.component_id in self._state:
                continue

            if hasattr(component, "extra_context"):
                extra_context = component.extra_context
                component.extra_context = None
            else:
                extra_context = None

            request = component.request
            component.request = None

            self._state[component.component_id] = (
                component,
                request,
                extra_context,
                component.parent,
                component.children.copy(),
            )

            if component.parent:
                components.append(component.parent)
                component.parent = PointerUnicornView(component.parent.component_cache_key)

            for index, child in enumerate(component.children):
                components.append(child)
                component.children[index] = PointerUnicornView(child.component_cache_key)

        for component, *_ in self._state.values():
            try:
                pickle.dumps(component)
            except (
                TypeError,
                AttributeError,
                NotImplementedError,
                pickle.PicklingError,
            ) as e:
                raise UnicornCacheError(
                    f"Cannot cache component '{type(component)}' because it is not picklable: {type(e)}: {e}"
                ) from e

        return self

    def __exit__(self, *args):
        for component, request, extra_context, parent, children in self._state.values():
            component.request = request
            component.parent = parent
            component.children = children

            if extra_context:
                component.extra_context = extra_context

    def components(self) -> List["django_unicorn.views.UnicornView"]:
        return [component for component, *_ in self._state.values()]


def cache_full_tree(component: "django_unicorn.views.UnicornView"):
    root = component

    while root.parent:
        root = root.parent

    cache = caches[get_cache_alias()]

    with CacheableComponent(root) as caching:
        for component in caching.components():
            cache.set(component.component_cache_key, component)


def restore_from_cache(component_cache_key: str, request: HttpRequest = None) -> "django_unicorn.views.UnicornView":
    """
    Gets a cached unicorn view by key, restoring and getting cached parents and children
    and setting the request.
    """

    cache = caches[get_cache_alias()]
    cached_component = cache.get(component_cache_key)

    if cached_component:
        roots = {}
        root: "django_unicorn.views.UnicornView" = cached_component
        roots[root.component_cache_key] = root

        while root.parent:
            root = cache.get(root.parent.component_cache_key)
            roots[root.component_cache_key] = root

        to_traverse: List["django_unicorn.views.UnicornView"] = []
        to_traverse.append(root)

        while to_traverse:
            current = to_traverse.pop()
            current.setup(request)
            current._validate_called = False
            current.calls = []

            for index, child in enumerate(current.children):
                key = child.component_cache_key
                cached_child = roots.pop(key, None) or cache.get(key)

                cached_child.parent = current
                current.children[index] = cached_child
                to_traverse.append(cached_child)

    return cached_component
