from typing import Any

from django_unicorn.call_method_parser import parse_call_method_name


class Action:
    """
    Base class for all actions.
    """

    __slots__ = ("action_type", "partials", "payload")

    def __init__(self, data: dict[str, Any]):
        self.action_type = data.get("type")
        self.payload = data.get("payload", {})
        self.partials = data.get("partials", [])
        # Handle deprecated 'partial'
        if "partial" in data:
            self.partials.append(data["partial"])

    def __repr__(self):
        return f"Action(type='{self.action_type}', payload={self.payload})"


class SyncInput(Action):
    __slots__ = ("name", "value")

    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.name = self.payload.get("name")
        self.value = self.payload.get("value")

    def __repr__(self):
        return f"SyncInput(name='{self.name}', value='{self.value}')"


class CallMethod(Action):
    __slots__ = ("args", "kwargs", "method_name")

    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        call_method_name = self.payload.get("name", "")
        self.method_name, self.args, kwargs = parse_call_method_name(call_method_name)
        self.kwargs = dict(kwargs)

    def __repr__(self):
        return f"CallMethod(method_name='{self.method_name}', args={self.args}, kwargs={self.kwargs})"


class Reset(Action):
    __slots__ = ()

    def __repr__(self):
        return "Reset()"


class Refresh(Action):
    __slots__ = ()

    def __repr__(self):
        return "Refresh()"


class Toggle(Action):
    __slots__ = ("args", "kwargs", "method_name")

    def __init__(self, data: dict[str, Any]):
        # We need to parse args similar to CallMethod
        super().__init__(data)
        call_method_name = self.payload.get("name", "")
        self.method_name, self.args, kwargs = parse_call_method_name(call_method_name)
        self.kwargs = dict(kwargs)

    def __repr__(self):
        return f"Toggle(args={self.args})"
