import sys
from unittest.mock import MagicMock, patch

import pytest
from django.core.cache import caches

from django_unicorn.views.message import UnicornMessageHandler
from django_unicorn.views.queue import ComponentRequestQueue


# Create fake request class that is pickleable
class FakeAction:
    def __init__(self, action_type="syncInput", payload=None, partials=None):
        self.action_type = action_type
        self.payload = payload or {}
        self.partials = partials or []


class FakeRequest:
    __hash__ = None

    def __init__(self, component_id, epoch, data, action_queue=None):
        self.id = component_id
        self.epoch = epoch
        self.data = data
        self.action_queue = action_queue or []
        self.request = None  # To mimic real ComponentRequest
        self.name = "test_component"

    def __eq__(self, other):
        if not isinstance(other, FakeRequest):
            return False
        return self.id == other.id and self.epoch == other.epoch and self.data == other.data

    def __repr__(self):
        return f"FakeRequest(id={self.id}, epoch={self.epoch}, data={self.data})"


@pytest.mark.django_db
def test_race_condition_dropped_request_bug(settings):
    # Ensure serial enabled
    settings.UNICORN["SERIAL"]["ENABLED"] = True

    cache = caches["default"]
    cache.clear()

    # Setup queue
    component_id = "test_id"
    queue = ComponentRequestQueue(component_id)

    req1 = FakeRequest(component_id=component_id, epoch=100, data={"count": 1})
    req2 = FakeRequest(component_id=component_id, epoch=200, data={"count": 2})

    # Scenario: Req2 arrived first, then Req1.
    # Cache queue: [Req2, Req1]
    # Note: Req2 is at index 0, Req1 at index 1.
    queue.add(req2)
    queue.add(req1)

    handler = UnicornMessageHandler(MagicMock())

    message_module = sys.modules["django_unicorn.views.message"]

    # Mock ActionDispatcher on the module directly to avoid import path issues
    with patch.object(message_module, "ActionDispatcher") as mock_dispatcher_cls:
        mock_dispatcher_instance = mock_dispatcher_cls.return_value
        mock_dispatcher_instance.dispatch.return_value = {"data": {}}

        handler._handle_queued_component_requests(queue)

        # Verify calls
        # mock_dispatcher_cls calls: call(request, component_request)

        assert mock_dispatcher_cls.call_count >= 2

        call_epochs = [call.args[1].epoch for call in mock_dispatcher_cls.call_args_list]

        assert 200 in call_epochs, f"Req2 (Epoch 200) was dropped! calls: {call_epochs}"
        assert call_epochs == [100, 200], f"Wrong order or dropped calls: {call_epochs}"
