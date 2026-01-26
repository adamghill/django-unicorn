import pytest
from tests.views.message.utils import post_and_get_response

from django_unicorn.components import UnicornView
from example.coffee.models import Flavor, Taste


class M2MComponent(UnicornView):
    template_name = "templates/test_component.html"
    taste: Taste | None = None

    def mount(self):
        if self.component_args:
             self.taste = Taste.objects.get(pk=self.component_args[0])

    def refresh(self):
        # usage: unicorn:poll="refresh"
        if self.taste:
            self.taste = Taste.objects.get(pk=self.taste.pk)

@pytest.mark.django_db
def test_m2m_overwriting(client):
    # Setup
    flavor1 = Flavor.objects.create(name="Flavor 1")
    flavor2 = Flavor.objects.create(name="Flavor 2")
    taste = Taste.objects.create(name="Test Taste")
    taste.flavor.add(flavor1)

    # Initial state (client side)
    # We strictly define what we expect the client state to resemble after initial render
    # 'flavor' is M2M. Unicorn serialization of M2M depends on configuration/implementation.
    # Attempting to mimic the "stale" state on the client.
    # If Unicorn serializes M2M as list of PKs:
    data = {"taste": {"pk": taste.pk, "flavor": [flavor1.pk]}}

    # 2. Modify DB (Admin action) - Add Flavor 2
    taste.flavor.add(flavor2)
    assert taste.flavor.count() == 2

    # 3. Component Update (Poll/Refresh)
    # Client sends back the OLD data (only flavor1 in the payload)
    # This simulates the frontend sending back its known state which is outdated.
    action_queue = [{"payload": {"name": "refresh"}, "type": "callMethod"}]

    response = post_and_get_response(
        client,
        url="/message/tests.views.test_m2m_overwriting.M2MComponent",
        data=data,
        action_queue=action_queue,
    )

    assert not response.get("errors")

    # 4. Assert DB state
    taste.refresh_from_db()

    # If the bug exists, Flavor 2 might vary well be gone because the component
    # restored the 'taste' model from the 'data' (which only had flavor1)
    # and saved it or synced the M2M.
    assert taste.flavor.count() == 2, "DB M2M changes were overwritten!"
    assert flavor2 in taste.flavor.all()
