from typing import Any

from bs4 import BeautifulSoup, Tag

from django_unicorn.components import UnicornView
from django_unicorn.components.unicorn_template_response import get_root_element
from django_unicorn.errors import RenderNotModifiedError
from django_unicorn.serializer import loads
from django_unicorn.utils import generate_checksum
from django_unicorn.views.request import ComponentRequest


class ComponentResponse:
    __slots__ = ("component", "component_request", "partials", "return_data")

    def __init__(
        self,
        component: UnicornView,
        component_request: ComponentRequest,
        return_data: Any | None = None,
        partials: list[dict[str, Any]] | None = None,
    ):
        self.component = component
        self.component_request = component_request
        self.return_data = return_data
        self.partials = partials or []

    def get_data(self) -> dict[str, Any]:
        # Sort data so it's stable
        self.component_request.data = {
            key: self.component_request.data[key] for key in sorted(self.component_request.data)
        }

        result = {
            "id": self.component_request.id,
            "data": self.component_request.data,
            "errors": self.component.errors,
            "calls": self.component.calls,
            "checksum": generate_checksum(self.component_request.data),
        }

        render_not_modified = False
        soup = None
        soup_root = None
        rendered_component = self.component.last_rendered_dom

        if self.partials:
            result.update({"partials": self.partials})
        else:
            rendered_component_hash = generate_checksum(rendered_component)

            if (
                self.component_request.hash == rendered_component_hash
                and (not self.return_data or not self.return_data.value)
                and not self.component.calls
            ):
                if not self.component.parent and self.component.force_render is False:
                    raise RenderNotModifiedError()
                else:
                    render_not_modified = True

            # Make sure that partials with comments or blank lines before the root element
            # only return the root element
            soup = BeautifulSoup(rendered_component, features="html.parser")
            soup_root = get_root_element(soup)
            rendered_component = str(soup_root)

            result.update(
                {
                    "dom": rendered_component,
                    "hash": rendered_component_hash,
                }
            )

        if self.return_data:
            result.update(
                {
                    "return": self.return_data.get_data(),
                }
            )

            if self.return_data.redirect:
                result.update(
                    {
                        "redirect": self.return_data.redirect,
                    }
                )

            if self.return_data.poll:
                result.update(
                    {
                        "poll": self.return_data.poll,
                    }
                )

        parent_component = self.component.parent
        parent_result = result

        while parent_component:
            if parent_component.force_render is True:
                # TODO: Should parent_component.hydrate() be called?
                parent_frontend_context_variables = loads(parent_component.get_frontend_context_variables())
                parent_checksum = generate_checksum(str(parent_frontend_context_variables))

                parent = {
                    "id": parent_component.component_id,
                    "checksum": parent_checksum,
                }

                if not self.partials:
                    parent_dom = parent_component.render()
                    self.component.parent_rendered(parent_dom)

                    # Get re-generated child checksum and update the child component inside the parent DOM
                    if not soup_root:
                        raise AssertionError("Missing root element")

                    # TODO: Use minestrone for this
                    child_soup_checksum = soup_root.attrs["unicorn:checksum"]
                    child_soup_unicorn_id = soup_root.attrs["unicorn:id"]

                    parent_soup = BeautifulSoup(parent_dom, features="html.parser")

                    for _child in parent_soup.descendants:
                        if isinstance(_child, Tag) and child_soup_unicorn_id == _child.attrs.get("unicorn:id"):
                            _child.attrs["unicorn:checksum"] = child_soup_checksum

                    parent_soup = get_root_element(parent_soup)
                    parent_dom = str(parent_soup)

                    # Remove the child DOM from the payload since the parent DOM supersedes it
                    result["dom"] = None

                    parent.update(
                        {
                            "dom": parent_dom,
                            "data": parent_frontend_context_variables,
                            "errors": parent_component.errors,
                            "hash": generate_checksum(parent_dom),
                        }
                    )

                if render_not_modified:
                    # TODO: Determine if all parents have not changed and return a 304 if
                    # that's the case
                    pass

                parent_result.update({"parent": parent})
                parent_result = parent

            self.component = parent_component
            parent_component = parent_component.parent

        return result
