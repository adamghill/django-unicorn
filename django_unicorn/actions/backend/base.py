
from abc import ABC, abstractmethod

from django_unicorn.components import Component


class BackendAction(ABC):
    """
    Abstract base class for Unicorn Actions that get queued & applied to components
    in the backend (via python). This base class also has helper methods for 
    dynamically loading various Action types.
    
    This class and its methods are typically handled by the FrontendAction class
    """

    # --- Abstract methods / attrs that must be set in the subclass ---

    action_type: str = None
    """
    A name for this action that is used in JSON from the frontend
    """

    @abstractmethod
    def apply(
            self,
            component: Component,
            request, # : ComponentRequest,
        ) -> tuple:  # returns a tuple of an FrontendAction + a new Component w. updates
        """
        Applies the update to the component and returns the ActionResult if
        there is one. Must be defined in all subclasses.
        """
        raise NotImplementedError()

    # --- Built-in methods ---

    def __init__(self, payload: dict, partials: list):
        self.payload = payload
        self.partials = partials

    def __repr__(self):
        return (
            f"BackEnd Action: {self.__class__.__name__}"
            f"(action_type='{self.action_type}' payload={self.payload} "
            f"partials={self.partials})"
        )

    def to_dict(self) -> dict:
        """
        Converts the Action back to a dictionary match what the frontend gives
        """
        return {
            "partials": self.partials,
            "payload": self.payload,
            "type": self.action_type,
        }

    @classmethod
    def from_dict(cls, data: dict):
        expected_type = data.get("type")
        if expected_type != cls.action_type:
            raise ValueError(
                f"Action type mismatch. Type '{expected_type}' "
                f"was provided, but class only accepts '{cls.action_type}'"
            )
        return cls(
            payload = data.get("payload", {}),
            partials = data.get("partials", []),
        )

    # --- Utility methods that help interact with *all* Action subclasses ---

    @classmethod
    def from_many_dicts(cls, data: list[dict]):
        """
        Given a list of config dictionaries, this will create and return
        a list Action objects in the proper Action subclass.
        
        This input is typically grabbed directly from `request.body.actionQueue`
        """

        mappings = cls.get_action_type_mappings()

        actions = []
        for config in data:
            action_type = config["type"]

            if action_type not in mappings.keys():
                raise ValueError(f"Unknown Action type: '{action_type}'")

            action_class = mappings[action_type]
            action = action_class.from_dict(config)
            actions.append(action)

        return actions


    def get_action_type_mappings() -> dict:
        """
        Gives a mapping of action_type to the Action subclass that should be
        used. For example: {"callMethod": django_unicorn.actions.CallMethod}
        """
        # TODO: We assume only internal Actions for now, but we may want to
        # support customer user Actions.

        # local import to prevent circular deps
        from django_unicorn.actions import (
            CallMethod,
            SyncInput,
        )

        return {
            action.action_type: action
            for action in [
                CallMethod,
                SyncInput,
                # !!! These are special cases.
                # See CallMethod.from_dict for details.
                #   Refresh,
                #   Reset,
                #   Toggle,
                #   Validate,
            ]
        }
