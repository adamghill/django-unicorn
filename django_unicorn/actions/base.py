# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from django_unicorn.components import Component


class Action(ABC):
    """
    Abstract base class for Unicorn Actions that get queued. Also contains
    helper methods for dynamically loading various Action types
    """
    
    # --- Abstract methods / attrs that must be set in the subclass ---
    
    action_type: str = None
    """
    A name for this action that is used in JSON from the frontend
    """
    
    @abstractmethod
    def apply(self, component: Component) -> "ActionResult":
        """
        Applies the update to the component and returns the ActionResult if
        there is one. Must be defined in all subclasses
        """
        raise NotImplementedError()
    
    # --- Built-in methods ---

    def __init__(self, payload: dict, partials: list):
        self.payload = payload
        self.partials = partials
    
    def __repr__(self):
        # TODO: consider updating to match subclassing
        return f"Action(action_type='{self.action_type}' payload={self.payload} partials={self.partials})"

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
            # !!! These are special cases. See CallMethod.from_dict for details
            # Refresh,
            # Reset,
            # Toggle,
            # Validate,
        )

        return {
            action.action_type: action
            for action in [
                CallMethod,
                SyncInput,
                # Refresh,
                # Reset,
                # Toggle,
                # Validate,
            ]
        }


class ActionResult:
    """
    The return value of Action (if one is given). Typically comes from 
    a CallMethodAction or something similar
    """
    
    def __init__(self, method_name, args=None, kwargs=None):
        self.method_name = method_name
        self.args = args or []
        self.kwargs = kwargs or {}
        self._value = {}
        self.redirect = {}
        self.poll = {}

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        # TODO: Support a tuple/list return_value which could contain multiple values

        if value is not None:
            if isinstance(value, HttpResponseRedirect):
                self.redirect = {
                    "url": value.url,
                }
            elif isinstance(value, HashUpdate):
                self.redirect = {
                    "hash": value.hash,
                }
            elif isinstance(value, LocationUpdate):
                self.redirect = {
                    "url": value.redirect.url,
                    "refresh": True,
                    "title": value.title,
                }
            elif isinstance(value, PollUpdate):
                self.poll = value.to_json()

            if self.redirect:
                self._value = self.redirect

    def get_data(self):
        try:
            serialized_value = loads(dumps(self.value))
            serialized_args = loads(dumps(self.args))
            serialized_kwargs = loads(dumps(self.kwargs))

            return {
                "method": self.method_name,
                "args": serialized_args,
                "kwargs": serialized_kwargs,
                "value": serialized_value,
            }
        except Exception as e:
            logger.exception(e)

        return {}
