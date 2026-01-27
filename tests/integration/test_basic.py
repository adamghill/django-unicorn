"""
Playwright integration tests for django-unicorn example app.

These tests require the example app to be running on localhost:8080.
Start it with: just runserver

These tests verify actual reactivity - that when inputs change, the DOM updates accordingly.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = [
    pytest.mark.integration,
    pytest.mark.playwright,
]

BASE_URL = "http://localhost:8080"


class TestHomepage:
    """Tests for the homepage."""

    def test_homepage_loads(self, page: Page):
        """Test that the homepage loads and contains expected content."""
        page.goto(BASE_URL, timeout=60000)
        expect(page).to_have_title("django-unicorn examples")
        expect(page.locator("body")).to_contain_text("unicorn")


class TestTextInputsComponent:
    """Tests for the text-inputs component with unicorn:model binding."""

    def test_input_updates_display(self, page: Page):
        """Test that typing in an input updates the displayed text."""
        page.goto(f"{BASE_URL}/text-inputs", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Get the first component on the page
        component = page.locator("[unicorn\\:id]").first

        # The component displays "Hello {{ name|title }}" - initially "Hello World"
        expect(component.locator("text=Hello World")).to_be_visible()

        # Find a text input with unicorn:model="name" that doesn't have partial updates
        # The first one (nth 0) has u:partial.id="model-id" which would prevent the greeting from updating
        text_input = component.locator("input[unicorn\\:model='name']").nth(1)
        expect(text_input).to_be_visible()

        # Clear and type a new name
        text_input.fill("")
        text_input.fill("Playwright")

        # Blur to trigger the model update
        text_input.blur()

        # Wait for the server response and DOM update
        page.wait_for_timeout(2000)

        # The greeting should now show "Hello Playwright"
        expect(component.locator("text=Hello Playwright")).to_be_visible()

    def test_button_click_updates_name(self, page: Page):
        """Test that clicking a button updates the name via setter."""
        page.goto(f"{BASE_URL}/text-inputs", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Get the first component
        component = page.locator("[unicorn\\:id]").first

        # Find the button that sets name to 'human' (use first to handle multiple)
        button = component.locator("button:has-text(\"name='human'\")").first
        expect(button).to_be_visible()

        # Click the button
        button.click()

        # Wait for update
        page.wait_for_timeout(1500)

        # Verify the greeting updated within this component
        expect(component.locator("text=Hello Human")).to_be_visible()

    def test_reset_button_restores_initial_state(self, page: Page):
        """Test that the $reset button restores the component to initial state."""
        page.goto(f"{BASE_URL}/text-inputs", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Get the first component
        component = page.locator("[unicorn\\:id]").first

        # Change the name first
        button = component.locator("button:has-text(\"name='human'\")").first
        button.click()
        page.wait_for_timeout(1500)

        # Verify name changed
        expect(component.locator("text=Hello Human")).to_be_visible()

        # Click reset (the reset button text is exactly "Reset the component")
        reset_button = component.locator("button:has-text('Reset the component')")
        reset_button.click()
        page.wait_for_timeout(1500)

        # Verify name is back to "World"
        expect(component.locator("text=Hello World")).to_be_visible()


class TestValidationComponent:
    """Tests for the validation component."""

    def test_text_input_updates_display(self, page: Page):
        """Test that changing text input updates the displayed value."""
        page.goto(f"{BASE_URL}/validation", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Initial state - component shows {{ text }}: hello
        component = page.locator("[unicorn\\:id]").first
        expect(component.locator("text=: hello")).to_be_visible()

        # Find the text input by ID
        text_input = page.locator("#textId")
        expect(text_input).to_be_visible()

        # Clear and type new value
        text_input.fill("")
        text_input.fill("testing")
        text_input.blur()

        # Wait for update
        page.wait_for_timeout(1500)

        # The displayed value should update
        expect(component.locator("text=: testing")).to_be_visible()

    def test_button_click_sets_text(self, page: Page):
        """Test that clicking set_text_no_validation updates text."""
        page.goto(f"{BASE_URL}/validation", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        component = page.locator("[unicorn\\:id]").first

        # Click the button
        button = page.locator("button:has-text('set_text_no_validation()')")
        button.click()

        # Wait for update
        page.wait_for_timeout(1500)

        # Text should be "no validation"
        expect(component.locator("text=: no validation")).to_be_visible()

    def test_reset_restores_initial_state(self, page: Page):
        """Test that $reset restores component to initial state."""
        page.goto(f"{BASE_URL}/validation", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        component = page.locator("[unicorn\\:id]").first

        # Change the text
        text_input = page.locator("#textId")
        text_input.fill("changed")
        text_input.blur()
        page.wait_for_timeout(1500)

        # Verify it changed - look for the changed text
        expect(component.locator("text=: changed")).to_be_visible()

        # Click reset - there are two reset buttons, pick the first one
        reset_button = page.locator("button:has-text('$reset')").first
        reset_button.click()
        page.wait_for_timeout(1500)

        # Verify it's back to "hello"
        expect(component.locator("text=: hello")).to_be_visible()


class TestPollingComponent:
    """Tests for the polling component."""

    def test_polling_page_loads(self, page: Page):
        """Test that the polling page loads with a component."""
        page.goto(f"{BASE_URL}/polling", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Component should be visible
        component = page.locator("[unicorn\\:id]").first
        expect(component).to_be_visible()


class TestModelsComponent:
    """Tests for the models component."""

    def test_models_page_loads(self, page: Page):
        """Test that the models page loads with a component."""
        page.goto(f"{BASE_URL}/models", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Component should be visible
        component = page.locator("[unicorn\\:id]").first
        expect(component).to_be_visible()


class TestHtmlInputsComponent:
    """Tests for the html-inputs component."""

    def test_html_inputs_page_loads(self, page: Page):
        """Test that the html-inputs page loads with a component."""
        page.goto(f"{BASE_URL}/html-inputs", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Component should be visible
        component = page.locator("[unicorn\\:id]").first
        expect(component).to_be_visible()


class TestDirectView:
    """Tests for direct view components."""

    def test_direct_view_loads(self, page: Page):
        """Test that direct view page loads correctly."""
        page.goto(f"{BASE_URL}/direct-view", timeout=60000)

        # Wait for component to initialize
        page.wait_for_selector("[unicorn\\:id]", timeout=10000)

        # Component should be visible
        component = page.locator("[unicorn\\:id]").first
        expect(component).to_be_visible()
