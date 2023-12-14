from unittest.mock import MagicMock

from django_unicorn.cacher import (
    CacheableComponent,
    cache_full_tree,
    restore_from_cache,
)
from django_unicorn.components import UnicornView


class FakeComponent(UnicornView):
    pass


def test_cacheable_component_request_is_none_then_restored():
    component = FakeComponent(component_id="asdf123498", component_name="hello-world")
    request = component.request = MagicMock()
    assert component.request

    with CacheableComponent(component):
        assert component.request is None

    assert component.request == request


def test_cacheable_component_extra_context_is_none_then_restored():
    component = FakeComponent(component_id="asdf123499", component_name="hello-world")
    extra_context = component.extra_context = MagicMock()
    assert component.extra_context

    with CacheableComponent(component):
        assert component.extra_context is None

    assert component.extra_context == extra_context


def test_cacheable_component_parents_have_request_restored():
    component = FakeComponent(component_id="asdf123498", component_name="hello-world")
    component2 = FakeComponent(component_id="asdf123499", component_name="hello-world", parent=component)
    component3 = FakeComponent(component_id="asdf123500", component_name="hello-world", parent=component2)
    request = MagicMock()
    extra_content = "extra_content"
    for c in [component, component2, component3]:
        c.request = request
        c.extra_context = extra_content

    with CacheableComponent(component3):
        assert component.request is None
        assert component2.request is None
        assert component3.request is None
        assert component.extra_context is None
        assert component2.extra_context is None
        assert component3.extra_context is None

    assert component.request == request
    assert component2.request == request
    assert component3.request == request
    assert component.extra_context == extra_content
    assert component2.extra_context == extra_content
    assert component3.extra_context == extra_content


def test_restore_cached_component_children_have_request_set():
    component = FakeComponent(component_id="asdf123498", component_name="hello-world")
    component2 = FakeComponent(component_id="asdf123499", component_name="hello-world")
    component3 = FakeComponent(component_id="asdf123500", component_name="hello-world")
    component4 = FakeComponent(component_id="asdf123501", component_name="hello-world")
    component3.children.append(component4)
    component.children.extend([component2, component3])
    request = MagicMock()
    extra_content = "extra_content"
    for c in [component, component2, component3, component4]:
        c.request = request
        c.extra_context = extra_content

    with CacheableComponent(component):
        assert component.request is None
        assert component2.request is None
        assert component3.request is None
        assert component4.request is None
        assert component.extra_context is None
        assert component2.extra_context is None
        assert component3.extra_context is None
        assert component4.extra_context is None

    assert component.request == request
    assert component2.request == request
    assert component3.request == request
    assert component4.request == request
    assert component.extra_context == extra_content
    assert component2.extra_context == extra_content
    assert component3.extra_context == extra_content
    assert component4.extra_context == extra_content


class ExampleCachingComponent(UnicornView):
    name = "World"

    def get_name(self):
        return "World"

    def __str__(self):
        return f"ECC {self.component_id} - {self.component_name}"


def test_caching_components(settings):
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
    settings.UNICORN["CACHE_ALIAS"] = "default"
    root = ExampleCachingComponent(component_id="rrr", component_name="root")
    child1 = ExampleCachingComponent(component_id="1111", component_name="child1", parent=root)
    child2 = ExampleCachingComponent(component_id="2222", component_name="child2", parent=root)
    child3 = ExampleCachingComponent(component_id="3333", component_name="child3", parent=root)
    grandchild = ExampleCachingComponent(component_id="4444", component_name="grandchild", parent=child1)
    grandchild2 = ExampleCachingComponent(component_id="5555", component_name="grandchild2", parent=child1)
    grandchild3 = ExampleCachingComponent(component_id="6666", component_name="grandchild3", parent=child3)

    cache_full_tree(child3)
    request = MagicMock()

    restored: UnicornView = restore_from_cache(child2.component_cache_key, request)

    restored_root = restored
    while restored_root.parent:
        restored_root = restored_root.parent

    assert root.component_id == restored_root.component_id
    assert 3 == len(restored_root.children)
    for i, child in enumerate([child1, child2, child3]):
        assert restored_root.children[i].component_id == child.component_id
    assert 2 == len(restored_root.children[0].children)
    for i, child in enumerate([grandchild, grandchild2]):
        assert restored_root.children[0].children[i].component_id == child.component_id
    assert not restored_root.children[1].children
    assert 1 == len(restored_root.children[2].children)
    assert grandchild3.component_id == restored_root.children[2].children[0].component_id
