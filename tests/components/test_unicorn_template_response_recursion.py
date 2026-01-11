import pickle
import sys
from unittest.mock import MagicMock

from bs4 import BeautifulSoup
from django.test import RequestFactory

from django_unicorn.components import UnicornView
from django_unicorn.components.unicorn_template_response import UnicornTemplateResponse


class RecursionComponent(UnicornView):
    template_name = "templates/test_component.html"
    pass


def test_child_component_cleanup_prevents_recursion_error():
    # 1. Create child component and simulate it having a large _json_tag (as if rendered)
    child = RecursionComponent(component_name="child", component_id="child_id")

    # Create a deep DOM to ensure recursion error would happen if not cleaned up
    depth = 2000
    html_content = "<div>" + ("<span>" * depth) + "Hello" + ("</span>" * depth) + "</div>"
    soup = BeautifulSoup(html_content, "html.parser")
    child._json_tag = soup.find("div")  # Simulate the tag attached during child render
    child._init_script = "Unicorn.componentInit({});"

    # 2. Create parent component and link child
    parent = RecursionComponent(component_name="parent", component_id="parent_id")
    parent.children.append(child)

    # 3. Setup UnicornTemplateResponse for parent
    request = RequestFactory().get("/")
    template = MagicMock()
    template.render.return_value = "<html><body><div unicorn:view>Parent Content</div></body></html>"

    response = UnicornTemplateResponse(
        template=template,
        request=request,
        component=parent,
        init_js=True,  # Important to trigger the logic that collects json_tags
    )

    # Increase recursion limit to allow BS4 to process the deep tree without crashing during render
    # We want to verify that pickling works AFTER the tag is removed, not that BS4 crashes.
    original_recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)

    try:
        # 4. Render the parent
        # This should trigger the loop that collects children's json_tags and DELETES them
        response.render()

        # 5. Verify _json_tag is deleted from child
        assert not hasattr(child, "_json_tag"), "child._json_tag should have been deleted"

        # 6. Verify pickling parent works
        # If _json_tag was arguably still there, this might fail or pass depending on limit.
        # But since we verified it IS deleted, this confirms the object state is clean.
        pickle.dumps(parent)

    finally:
        sys.setrecursionlimit(original_recursion_limit)
