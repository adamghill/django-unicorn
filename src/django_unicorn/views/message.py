import copy
import logging

from django.http import HttpRequest

from django_unicorn.errors import RenderNotModifiedError, UnicornViewError
from django_unicorn.settings import get_serial_enabled
from django_unicorn.views.action_dispatcher import ActionDispatcher
from django_unicorn.views.queue import ComponentRequestQueue, RequestMerger
from django_unicorn.views.request import ComponentRequest

logger = logging.getLogger(__name__)


class UnicornMessageHandler:
    def __init__(self, request: HttpRequest):
        self.request = request

    def handle(self, component_request: ComponentRequest) -> dict:
        if not get_serial_enabled():
            return ActionDispatcher(self.request, component_request).dispatch()

        queue = ComponentRequestQueue(component_request.id)

        # Add to queue (this clears the request object internally for pickling)
        component_request.request = None
        queue.add(component_request)

        all_requests = queue.get_all()

        if len(all_requests) > 1:
            original_epoch = all_requests[0].epoch
            return {
                "queued": True,
                "epoch": component_request.epoch,
                "original_epoch": original_epoch,
            }

        return self._handle_queued_component_requests(queue)

    def _handle_queued_component_requests(self, queue: ComponentRequestQueue) -> dict:
        requests = queue.get_all()

        if not requests:
            raise UnicornViewError(f"No request found for {queue.cache_key}")

        requests = sorted(requests, key=lambda r: r.epoch)
        first_request = requests[0]

        # Create a copy of the request before it is mutated by the dispatcher
        # This is required because the dispatcher modifies the request object in-place (e.g. data)
        # and the queue removal relies on the original object state (hash/pickle)
        request_to_remove = copy.deepcopy(first_request)

        first_request.request = self.request

        try:
            dispatcher = ActionDispatcher(self.request, first_request)
            result = dispatcher.dispatch()
        except RenderNotModifiedError:
            raise
        finally:
            queue.remove(request_to_remove)

        # Handle squashing of remaining requests
        remaining_requests = queue.get_all()
        if remaining_requests:
            if result and "data" in result:
                merged_request = RequestMerger.merge(remaining_requests[0], remaining_requests)
                merged_request.data.update(result["data"])

                # Clear queue of merged items
                for req in remaining_requests:
                    queue.remove(req)

                # Process merged request recursively
                merged_request.request = self.request
                return self.handle(merged_request)

        return result
