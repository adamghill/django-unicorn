

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

        self.action_queue = []
        for action_data in self.body.get("actionQueue", []):
            self.action_queue.append(Action(action_data))

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
        partials = [
            partial for action in self.action_queue for partial in action.partials
        ]

        # --- depreciated --
        # remove this section when partial is removed
        for action in self.action_queue:
            if action.partial:
                partials.append(action.partial)
        # --- depreciated ---

        return partials

    @property
    def action_types(self) -> bool:
        # OPTIMIZE: consider using @cached_property
        # Also maybe deprec if `Action` subclasses are made
        return [action.action_type for action in self.action_queue]

    @property
    def is_refresh_called(self) -> bool:
        return "$refresh" in self.action_types

    @property
    def is_reset_called(self) -> bool:
        return "$reset" in self.action_types

    @property
    def validate_all_fields(self) -> bool:
        return "$validate" in self.action_types

    @property
    def is_toggled(self) -> bool:
        return "$toggle" in self.action_types

    def apply_to_component(self, component):
        # OPTIMIZE: you *could* generate the ComponentResponse obj within
        # this update method. However, intertwining this would lead to less
        # maintainable code that is much more difficult to follow/understand.
        # Therefore, we save ComponentRequest for a separate method

        from django.forms import ValidationError
        from django.core.exceptions import NON_FIELD_ERRORS

        from django_unicorn.views.utils import set_property_from_data
        from django_unicorn.views.action_parsers import call_method, sync_input
        from django_unicorn.errors import UnicornViewError

        MIN_VALIDATION_ERROR_ARGS = 2

        for property_name, property_value in self.data.items():
            set_property_from_data(component, property_name, property_value)
        component.hydrate()

        # TODO: This section needs a refactor...

        return_data = None

        for action in self.action_queue:
            if action.action_type == "syncInput":
                sync_input.handle(self, component, action.payload)
            elif action.action_type == "callMethod":
                try:
                    # TODO: continue refactor of this method
                    (
                        component,
                        return_data,
                    ) = call_method.handle(self, component, action.payload)
                    self.action_results.append(return_data)
                except ValidationError as e:
                    if len(e.args) < MIN_VALIDATION_ERROR_ARGS or not e.args[1]:
                        raise AssertionError("Error code must be specified") from e

                    if hasattr(e, "error_list"):
                        error_code = e.args[1]

                        for error in e.error_list:
                            if NON_FIELD_ERRORS in component.errors:
                                component.errors[NON_FIELD_ERRORS].append(
                                    {"code": error_code, "message": error.message}
                                )
                            else:
                                component.errors[NON_FIELD_ERRORS] = [
                                    {"code": error_code, "message": error.message}
                                ]
                    elif hasattr(e, "message_dict"):
                        for field, message in e.message_dict.items():
                            if not e.args[1]:
                                raise AssertionError(
                                    "Error code must be specified"
                                ) from e

                            error_code = e.args[1]

                            if field in component.errors:
                                component.errors[field].append(
                                    {"code": error_code, "message": message}
                                )
                            else:
                                component.errors[field] = [
                                    {"code": error_code, "message": message}
                                ]
            else:
                raise UnicornViewError(f"Unknown action_type '{action.action_type}'")

        component.complete()

        # TODO: There should be a better place to call this...
        component._mark_safe_fields()

        return return_data