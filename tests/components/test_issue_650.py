from django.utils.functional import cached_property

from django_unicorn.components.unicorn_view import UnicornView, constructed_views_cache


class PropertyView(UnicornView):
    class Meta:
        javascript_exclude = ("user_id", "cached_user_id")

    @property
    def user_id(self):
        return self.request.user.id

    @cached_property
    def cached_user_id(self):
        return self.request.user.id


class User:
    id = 1


def test_issue_650_property_access_on_restore(settings, rf):
    request = rf.get("/")
    request.user = User()

    # Register component
    settings.UNICORN = {**settings.UNICORN, "COMPONENTS": {"property-view": PropertyView}}

    # 1. Create component
    component_id = "test-issue-650"
    component = UnicornView.create(component_id=component_id, component_name="property-view", request=request)

    assert component.user_id == 1
    assert component.cached_user_id == 1

    # Clear memory cache to force restore from backend cache (pickle)
    constructed_views_cache.clear()

    # 2. Restore component
    # We use the same request logic as if it was a new request
    request2 = rf.get("/")
    request2.user = User()

    component_restored = UnicornView.create(component_id=component_id, component_name="property-view", request=request2)

    # This fails if request is not set on restored component
    assert component_restored.user_id == 1
    # This also fails if request is not set AND it wasn't validly cached
    assert component_restored.cached_user_id == 1
