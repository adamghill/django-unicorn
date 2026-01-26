import copy
import logging

import orjson
from django.forms import ValidationError
from django.http import HttpRequest

from django_unicorn.components import UnicornView
from django_unicorn.components.unicorn_template_response import get_root_element
from django_unicorn.utils import html_element_to_string
from django_unicorn.views.request import ComponentRequest
from django_unicorn.views.response import ComponentResponse
from django_unicorn.views.utils import set_property_from_data

logger = logging.getLogger(__name__)


class ActionDispatcher:
    def __init__(self, request: HttpRequest, component_request: ComponentRequest):
        self.request = request
        self.component_request = component_request
        self.component = None
        self.partials = []
        self.return_data = None
        self.validate_all_fields = False
        self.is_refresh_called = False
        self.is_reset_called = False

    def dispatch(self) -> dict:
        self._create_component()
        self._hydrate()
        self._execute_actions()
        self._process_safe_fields()
        self._validate()
        rendered_component = self._render()
        return self._create_response(rendered_component)

    def _create_component(self):
        self.component = UnicornView.create(
            component_id=self.component_request.id,
            component_name=self.component_request.name,
            request=self.request,
        )

        # Ensure request is attached to the component and its parent
        if self.component.request is None:
            self.component.request = self.request
        if self.component.parent is not None and self.component.parent.request is None:
            self.component.parent.request = self.request

    def _hydrate(self):
        if self.component_request.data is None:
            raise AssertionError("Component request data is required")

        self.original_data = copy.deepcopy(self.component_request.data)

        self.component.pre_parse()

        for property_name, property_value in self.component_request.data.items():
            set_property_from_data(self.component, property_name, property_value)

        self.component.post_parse()
        self.component.hydrate()

    def _execute_actions(self):
        for action in self.component_request.action_queue:
            if action.partials:
                self.partials.extend(action.partials)

            try:
                result = action.handle(self.component_request, self.component)

                # Update state from result
                if result.component:
                    self.component = result.component

                self.is_refresh_called = self.is_refresh_called | result.is_refresh_called
                self.is_reset_called = self.is_reset_called | result.is_reset_called
                self.validate_all_fields = self.validate_all_fields | result.validate_all_fields
                if result.return_data:
                    self.return_data = result.return_data
            except ValidationError as e:
                self.component._handle_validation_error(e)

        self.component.complete()

    def _process_safe_fields(self):
        # Reload frontend context variables to capture changes
        self.component_request.data = orjson.loads(self.component.get_frontend_context_variables())
        self.component._handle_safe_fields()

    def _validate(self):
        # Calculate updated data to support partial validation
        updated_data = self.component_request.data
        if not self.is_reset_called:
            if not self.is_refresh_called:
                updated_data = {}
                for key, value in self.original_data.items():
                    if value != self.component_request.data.get(key):
                        updated_data[key] = self.component_request.data.get(key)

            if self.validate_all_fields:
                self.component.validate()
            else:
                self.component.validate(model_names=list(updated_data.keys()))

    def _render(self) -> str:
        if self.return_data and self.return_data.redirect:
            return ""

        rendered_component = self.component.render(request=self.request)
        self.component.rendered(rendered_component)
        return rendered_component

    def _create_response(self, rendered_component: str) -> dict:
        partial_doms = self._get_partial_doms(rendered_component) if rendered_component else []

        self.component.last_rendered_dom = rendered_component

        response = ComponentResponse(
            self.component, self.component_request, return_data=self.return_data, partials=partial_doms
        )
        return response.get_data()

    def _get_partial_doms(self, rendered_component: str) -> list[dict]:
        partial_doms = []
        if self.partials:
            soup = get_root_element(rendered_component)

            for partial in self.partials:
                target = partial.get("target") or partial.get("key") or partial.get("id")
                if not target:
                    raise AssertionError("Partial target is required")

                found = False
                if soup.get("unicorn:key") == target:
                    partial_doms.append({"key": target, "dom": html_element_to_string(soup, with_tail=False)})
                    found = True
                    continue

                if soup.get("id") == target:
                    partial_doms.append({"id": target, "dom": html_element_to_string(soup, with_tail=False)})
                    found = True
                    continue

                for element in soup.iter():
                    if element.get("unicorn:key") == target:
                        partial_doms.append({"key": target, "dom": html_element_to_string(element, with_tail=False)})
                        found = True
                        break

                if not found:
                    for element in soup.iter():
                        if element.get("id") == target:
                            partial_doms.append({"id": target, "dom": html_element_to_string(element, with_tail=False)})
                            found = True
                            break
        return partial_doms
