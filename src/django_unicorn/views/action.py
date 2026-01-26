from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from django_unicorn.call_method_parser import parse_call_method_name
from django_unicorn.components import UnicornView

if TYPE_CHECKING:
    from django_unicorn.views.request import ComponentRequest


@dataclass
class HandleResult:
    component: UnicornView
    is_refresh_called: bool = False
    is_reset_called: bool = False
    validate_all_fields: bool = False
    return_data: Any = None


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

    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return (
            self.action_type == other.action_type and self.payload == other.payload and self.partials == other.partials
        )

    __hash__ = None

    def to_json(self) -> dict:
        return {
            "type": self.action_type,
            "payload": self.payload,
            "partials": self.partials,
        }

    def handle(self, component_request: "ComponentRequest", component: UnicornView) -> HandleResult:
        from django_unicorn.views.action_parsers import sync_input  # noqa: PLC0415

        # Generic handler fallback
        if self.action_type == "syncInput":
            sync_input.handle(component_request, component, self.payload)
            return HandleResult(component=component)

        return HandleResult(component=component)


class SyncInput(Action):
    __slots__ = ("name", "value")

    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.name = self.payload.get("name")
        self.value = self.payload.get("value")

    def __repr__(self):
        return f"SyncInput(name='{self.name}', value='{self.value}')"

    def __eq__(self, other):
        if not isinstance(other, SyncInput):
            return False
        return super().__eq__(other) and self.name == other.name and self.value == other.value

    __hash__ = None

    def handle(self, component_request: "ComponentRequest", component: UnicornView) -> HandleResult:
        from django_unicorn.views.action_parsers import sync_input  # noqa: PLC0415

        sync_input.handle(component_request, component, self.payload)
        return HandleResult(component=component)


class CallMethod(Action):
    __slots__ = ("args", "kwargs", "method_name")

    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        call_method_name = self.payload.get("name", "")
        self.method_name, self.args, kwargs = parse_call_method_name(call_method_name)
        self.kwargs = dict(kwargs)

    def __repr__(self):
        return f"CallMethod(method_name='{self.method_name}', args={self.args}, kwargs={self.kwargs})"

    def __eq__(self, other):
        if not isinstance(other, CallMethod):
            return False
        return (
            super().__eq__(other)
            and self.method_name == other.method_name
            and self.args == other.args
            and self.kwargs == other.kwargs
        )

    __hash__ = None

    def handle(self, component_request: "ComponentRequest", component: UnicornView) -> HandleResult:
        from django_unicorn.views.action_parsers import call_method  # noqa: PLC0415

        (
            component,
            is_refresh_called,
            is_reset_called,
            validate_all_fields,
            return_data,
        ) = call_method.handle(component_request, component, self.payload)

        return HandleResult(
            component=component,
            is_refresh_called=is_refresh_called,
            is_reset_called=is_reset_called,
            validate_all_fields=validate_all_fields,
            return_data=return_data,
        )


class Reset(Action):
    __slots__ = ()

    def __repr__(self):
        return "Reset()"

    def __eq__(self, other):
        return isinstance(other, Reset) and super().__eq__(other)

    __hash__ = None

    def handle(self, component_request: "ComponentRequest", component: UnicornView) -> HandleResult:
        return CallMethod(self.to_json()).handle(component_request, component)


class Refresh(Action):
    __slots__ = ()

    def __repr__(self):
        return "Refresh()"

    def __eq__(self, other):
        return isinstance(other, Refresh) and super().__eq__(other)

    __hash__ = None

    def handle(self, component_request: "ComponentRequest", component: UnicornView) -> HandleResult:
        return CallMethod(self.to_json()).handle(component_request, component)


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

    def __eq__(self, other):
        if not isinstance(other, Toggle):
            return False
        return (
            super().__eq__(other)
            and self.method_name == other.method_name
            and self.args == other.args
            and self.kwargs == other.kwargs
        )

    __hash__ = None

    def handle(self, component_request: "ComponentRequest", component: UnicornView) -> HandleResult:
        return CallMethod(self.to_json()).handle(component_request, component)
