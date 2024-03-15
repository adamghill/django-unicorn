
import copy
from django_unicorn.errors import UnicornViewError
from django_unicorn.serializer import JSONDecodeError, loads
from django_unicorn.utils import generate_checksum
from django_unicorn.views.utils import set_property_from_data
from django_unicorn.views.response import ComponentResponse
from django_unicorn.components import Component
from django_unicorn.actions import (
    Action,
    ActionResult,
    CallMethod,
    Refresh,
    Reset,
    SyncInput,
    Toggle,
    Validate,
)


class ComponentRequest:
    """
    Parses, validates, and stores all of the data from the message request.
    """

    def __init__(self, request, component_name):
        self.body = {}
        self.request = request

        try:
            self.body = loads(request.body)

            if not self.body:
                raise AssertionError("Invalid JSON body")
        except JSONDecodeError as e:
            raise UnicornViewError("Body could not be parsed") from e

        self.name = component_name
        if not self.name:
            raise AssertionError("Missing component name")

        self.data = self.body.get("data")
        if not self.data is not None:
            raise AssertionError("Missing data")  # data could theoretically be {}

        self.id = self.body.get("id")
        if not self.id:
            raise AssertionError("Missing component id")

        self.epoch = self.body.get("epoch", "")
        if not self.epoch:
            raise AssertionError("Missing epoch")

        self.key = self.body.get("key", "")
        self.hash = self.body.get("hash", "")

        self.validate_checksum()
        
        action_configs = self.body.get("actionQueue", [])
        self.action_queue = Action.from_many_dicts(action_configs)

        # This is populated when `apply_to_component` is called.
        # `UnicornView.update_from_component_request` will also populate it.
        # It will have the same length as `self.action_queue` and map accordingly
        self.action_results = []

    def __repr__(self):
        return (
            f"ComponentRequest(name='{self.name}' id='{self.id}' key='{self.key}'"
            f" epoch={self.epoch} data={self.data} action_queue={self.action_queue} hash={self.hash})"
        )

    @property
    def has_been_applied(self) -> bool:
        """
        Whether this ComponentRequest and it's action_queue has been applied
        to a UnicornView component.
        """
        return True if self.action_results else False

    @property
    def has_action_results(self) -> bool:
        """
        Whether any return values in `action_results` need to be handled
        """
        if not self.has_been_applied:
            raise ValueError(
                "This ComponentRequest has not been applied yet, so "
                "no action_results are unavailable."
            )
        return True if any(self.action_results) else False

    def validate_checksum(self):
        """
        Validates that the checksum in the request matches the data.

        Returns:
            Raises `AssertionError` if the checksums don't match.
        """
        checksum = self.body.get("checksum")

        if not checksum:
            # TODO: Raise specific exception
            raise AssertionError("Missing checksum")

        generated_checksum = generate_checksum(self.data)

        if checksum != generated_checksum:
            # TODO: Raise specific exception
            raise AssertionError("Checksum does not match")

    @property
    def partials(self) -> bool:
        return [
            partial for action in self.action_queue for partial in action.partials
        ]
    
    # OPTIMIZE: consider using @cached_property
    @property
    def action_types(self) -> list[Action]:
        return [type(action) for action in self.action_queue]

    @property
    def includes_refresh(self) -> bool:
        return Refresh in self.action_types

    @property
    def includes_reset(self) -> bool:
        return Reset in self.action_types

    @property
    def includes_validate(self) -> bool:
        return Validate in self.action_types

    @property
    def includes_toggle(self) -> bool:
        return Toggle in self.action_types
    
    @property
    def includes_call_method(self) -> bool:
        return CallMethod in self.action_types
    
    @property
    def includes_sync_input(self) -> bool:
        return SyncInput in self.action_types

    def apply_to_component(
            self, 
            component: Component, 
            inplace: bool = False,
        ) -> Component:
        """
        Updates properties and applies all actions to the component, and
        then returns the updated component
        """
        # bug-check
        if self.has_been_applied:
            raise Exception(
                "This ComponentRequest was already applied to a Component. "
                "Ensure you are not performing duplicate work."
            )

        # set our objecto modify in-place below
        updated_component = component if inplace else copy.deepcopy(component)
        # OPTIMIZE: having inplace=False might be unnecessary overhead, but it
        # will help avoid complex bugs in the future
        
        # updates all component properties using data sent by request
        for property_name, property_value in self.data.items():
            set_property_from_data(
                updated_component, 
                property_name, 
                property_value,
            )

        updated_component.hydrate()

        # Apply all actions AND store the ActionResult objects to this Request
        # if any are returned.
        for action in self.action_queue: 
            # Action's apply methods can return several different types,
            # which tell us how to react. 
            action_result = action.apply(
                component=updated_component,
                request=self,  # only used by Reset & Refresh
            )
            if isinstance(action_result, Component):
                # If a Component is returned, then we've recieved some Action
                # that *replaces* our Component. This happens with Reset/Refresh
                updated_component = action_result
                self.action_results.append(None)
            elif isinstance(action_result, ActionResult):
                # These are actions like...
                #   HttpResponseRedirect, HashUpdate, LocationUpdate, PollUpdate
                # Which will need to be accessed when generating the response
                self.action_results.append(action_result)
            else:
                raise TypeError(
                    f"Unknown type returned from 'Action.apply': {type(action_result)}"
                )

        updated_component.complete()

        # !!! is there a better place to call this?
        updated_component._mark_safe_fields()
        
        return updated_component
