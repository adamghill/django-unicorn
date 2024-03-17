from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST

# !!! I think use of "View" and "Component" needs cleaned up accross classes + vars
# I'd vote for this renaming so that it matches other class names in django_unicorn
# This is a big change to core so I only demo it here for now.
from django_unicorn.components import UnicornView as Component
from django_unicorn.settings import (
    get_cache_alias,
    get_serial_enabled,
    get_serial_timeout,
)
from django_unicorn.views.request import ComponentRequest
from django_unicorn.views.response import ComponentResponse


@method_decorator(
    [
        # TODO: timed, handle_error, -> from django_unicorn.decorators import timed, handle_error
        ensure_csrf_cookie,
        csrf_protect,
        require_POST,
    ],
    name="dispatch",
)
class UnicornMessageHandler(View):
    def post(
        self,
        request: HttpRequest,
        component_name: str,
    ) -> JsonResponse:
        # OPTMIZE: consider making a middleware class that gives a
        # ComponentRequest input/subclass, rather than an HttpRequest.
        # (django-htmx can be used by example on how to do this)
        component_request = ComponentRequest(request, component_name)

        # check whether we are running things in serial (the default) or queueing
        use_queue = get_serial_enabled()
        if not use_queue:
            # handle immediately
            return self._get_response_from_request(component_request)
        else:
            # TEMP DISABLE
            raise NotImplementedError(
                "Queuing is temporarily disabled in django_unicorn as we undergo "
                "a larger refactor of our codebase. See issue #___ in our github "
                "repo to track the status of this feature."
            )
            # handle via queue
            return self._handle_queued_request(component_request)

    def _get_response_from_request(
        self,
        component_request: ComponentRequest,
    ) -> JsonResponse:
        """
        Given the ComponentRequest, this will generate the necessary JsonResponse
        to return to the frontend
        """

        updated_component = Component.from_request(
            component_request,
            apply_actions=True,
        )

        # bug-check
        assert component_request.has_been_applied
        
        breakpoint()  # current place in refactor

        # Now that we have our updated component and that our request has been
        # applied to it, the comparison of these two will tell us the proper
        # repsonse to give
        component_response = ComponentResponse.from_inspection(
            request=component_request,
            component=updated_component,
        )

        # returns either Component or ComponentReponse depending on 'return_response'
        return component_response.to_json_response()

    # -------------------------------------------------------------------------

    # CODE BELOW IS FOR QUEUED REQUESTS
    # !!! I have not started the refactor here, so queued requests are broken for now

    def _handle_component_request(self, component_request: ComponentRequest) -> dict:
        """
        Process a `ComponentRequest` by adding it to the cache and then either:
            - processing all of the component requests in the cache and returning the resulting value if
                it is the first component request for that particular component name + component id combination
            - return a `dict` saying that the request has been queued

        Args:
            param request: HttpRequest for the function-based view.
            param: component_request: Component request to process.

        Returns:
            `dict` with the following structure:
            {
                "id": component_id,
                "dom": html,  // re-rendered version of the component after actions in the payload are completed
                "data": {},  // updated data after actions in the payload are completed
                "errors": {},  // form validation errors
                "return": {}, // optional return value from an executed action
                "parent": {},  // optional representation of the parent component
            }
        """

        cache = caches[get_cache_alias()]

        # Add the current request `ComponentRequest` to the cache
        queue_cache_key = f"unicorn:queue:{component_request.id}"
        component_requests = cache.get(queue_cache_key) or []

        # Remove `request` from `ComponentRequest` before caching because it is not pickleable
        component_request.request = None
        component_requests.append(component_request)

        cache.set(
            queue_cache_key,
            component_requests,
            timeout=get_serial_timeout(),
        )

        if len(component_requests) > 1:
            original_epoch = component_requests[0].epoch
            return {
                "queued": True,
                "epoch": component_request.epoch,
                "original_epoch": original_epoch,
            }

        return self._handle_queued_component_requests(
            component_request.request,
            queue_cache_key,
        )

    def _handle_queued_component_requests(
        self,
        request: HttpRequest,
        queue_cache_key: str,
    ) -> dict:
        """
        Process the current component requests that are stored in cache.
        Also recursively checks for new requests that might have happened
        while executing the first request, merges them together and returns
        the correct appropriate data.

        Args:
            param request: HttpRequest for the view.
            param: queue_cache_key: Cache key created from component id which should be unique
                for any particular user's request lifecycle.

        Returns:
            JSON with the following structure:
            {
                "id": component_id,
                "dom": html,  // re-rendered version of the component after actions in the payload are completed
                "data": {},  // updated data after actions in the payload are completed
                "errors": {},  // form validation errors
                "return": {}, // optional return value from an executed action
                "parent": {},  // optional representation of the parent component
            }
        """
        cache = caches[get_cache_alias()]

        # Handle current request and any others in the cache by first sorting all of the current requests by ascending order
        component_requests = cache.get(queue_cache_key)

        if not component_requests or not isinstance(component_requests, list):
            raise UnicornViewError(f"No request found for {queue_cache_key}")

        component_requests = sorted(component_requests, key=lambda r: r.epoch)
        first_component_request = component_requests[0]

        try:
            # Can't store request on a `ComponentRequest` and cache it because `HttpRequest` isn't pickleable
            first_json_result = _process_component_request(
                request, first_component_request
            )
        except RenderNotModifiedError:
            # Catching this and re-raising, but need the finally clause to clear the cache
            raise
        finally:
            # Re-check for requests after the first request is processed
            component_requests = cache.get(queue_cache_key)

            # Check that the request is in the cache before popping it off
            if component_requests:
                component_requests.pop(0)
                cache.set(
                    queue_cache_key,
                    component_requests,
                    timeout=get_serial_timeout(),
                )

        if component_requests:
            # Create one new `component_request` from all of the queued requests that can be processed
            merged_component_request = None

            for additional_component_request in copy.deepcopy(component_requests):
                if merged_component_request:
                    # Add new component request action queue to the merged component request
                    merged_component_request.action_queue.extend(
                        additional_component_request.action_queue
                    )

                    # Originally, the thought was to merge the `additional_component_request.data` into
                    # the `merged_component_request.data`, but I can't figure out a way to do that in a sane
                    # manner. This means that for rapidly fired events that mutate `data`, that new
                    # `data` with be "thrown away".
                    # Relevant test: test_call_method_multiple.py::test_message_call_method_multiple_with_updated_data
                else:
                    merged_component_request = additional_component_request

                    # Set new component request data from the first component request's resulting data
                    for key, val in first_json_result.get("data", {}).items():
                        merged_component_request.data[key] = val

                component_requests.pop(0)
                cache.set(
                    queue_cache_key,
                    component_requests,
                    timeout=get_serial_timeout(),
                )

            merged_json_result = self._handle_component_request(
                request,
                merged_component_request,
            )

            return merged_json_result

        return first_json_result
