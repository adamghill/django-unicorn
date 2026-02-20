# Django Unicorn AGENTS.md

## Overview

`django-unicorn` is a reactive component framework for Django that allows developers to build full-stack interactive applications without needing a separate frontend framework like React, Vue, or Angular. It seamlessly integrates with Django's templates and views, bridging the gap between the backend and frontend.

**Philosophy**:
- **Full-Stack Django**: Keep logic in Python.
- **Convention over Configuration**: Uses strict naming conventions to wire components together.
- **No Build Step Required**: Works with vanilla Django templates (though JS can be minified).

## Architecture

Unicorn works by synchronizing the state between the backend Python view and the frontend DOM.

1.  **Initial Render**:
    - The `{% unicorn 'component-name' %}` template tag finds the matching `UnicornView` and template.
    - The view's public attributes are serialized into a JSON object.
    - The template is rendered with these attributes in the context.
    - The HTML and the initial JSON state are sent to the client.

2.  **Client-Side Initialization**:
    - `unicorn.js` (loaded via `{% unicorn_scripts %}`) behaves like a lightweight frontend framework.
    - It parses the DOM for `unicorn:` or `u:` attributes.
    - It binds event listeners (e.g., `click`, `input`, `blur`) to these elements.
    - It initializes the component state from the embedded JSON.

3.  **Interaction & Updates**:
    - When a user interacts (e.g., clicks a button, types in an input):
        - `unicorn.js` captures the event.
        - It sends an AJAX request to the Django backend with the component ID, the current data, and the action to perform.
    - **Server-Side Processing**:
        - Django restores the `UnicornView` state from the request data.
        - It executes the requested Python method (action).
        - It re-renders the component's template with the updated state.
    - **DOM Update**:
        - The server returns the new HTML and any updated data.
        - `unicorn.js` receives the response.
        - It uses `morphdom` to intelligently diff and patch the DOM, updating only the changed elements without losing focus or scroll position.

## Core Concepts

### Backend: `UnicornView`
Located in `src/django_unicorn/components/`.
- Inherits from `django_unicorn.components.UnicornView`.
- **State**: Public class attributes map directly to the frontend state.
- **Actions**: Methods explicitly callable from the template.
- **Lifecycle Hooks**:
    - `mount()`: Called on initialization.
    - `hydrate()`: Called when data is restored from the frontend.
    - `updating(name, value)` / `updated(name, value)`: Called around property changes.
- **Meta Options**:
    - `exclude`: Attributes to keep on the server only.
    - `javascript_exclude`: Attributes available in template but not serialized to JS.
    - `safe`: Attributes valid to render HTML (XSS prevention).

### Frontend: `unicorn.js`
Located in `src/django_unicorn/static/js/`.
- Handles connection to the backend.
- Parses `unicorn:model` for two-way data binding.
- Parses `unicorn:click`, `unicorn:change`, etc., for event binding.
- Manages the AJAX queue and DOM morphing.

### Template Tags
- `{% unicorn_scripts %}`: Injects the JavaScript library and initialization code.
- `{% unicorn 'component-name' %}`: Renders a component. Names are dash-cased (e.g., `hello-world`) which maps to `hello_world.HelloWorldView`.

## Directory Structure

- `src/django_unicorn/`: Core library code.
    - `components/`: Base `UnicornView` logic.
    - `views/`: AJAX endpoint handlers.
    - `serializer.py`: JSON serialization/deserialization logic.
    - `typer.py`: Type hinting and casting helpers.
    - `call_method_parser.py`: Parses string representations of method calls from templates.
    - `static/`: Frontend JavaScript assets.
- `example/`: A full Django project demonstrating usage.
    - `manage.py`: Standard Django entry point.
    - `www/`: Main app for the example project.
    - `unicorn/components/`: Example components (`hello_world.py`, etc.).
- `docs/`: Sphinx documentation.

## Development Workflow

The project uses `just` (a command runner) for common tasks.

- **Run Example Server**: `just runserver` (runs on port 8080).
- **Testing**:
    - Python: `just test-python` (uses `pytest`).
    - JavaScript: `just test-js` (uses `npm` tests).
    - Full Matrix: `just test-python-matrix` (uses `act` for local GitHub Actions).
- **Linting**: `just type` (uses `ruff` and `ty`).
- **Documentation**: `just docs-serve` (builds and serves Sphinx docs).

## Nuances & Limitations

1.  **Mutable Default Arguments**: A classic Python gotcha. Do **not** use `list = []` or `dict = {}` as class attributes in `UnicornView`. Initialize them in `mount()` instead to avoid shared state across users.
2.  **Serialization**: `django-unicorn` handles standard types (str, int, float, Decimal, bool), Django Models/QuerySets, Dataclasses, and Pydantic models. Complex custom objects need explicit serialization logic.
3.  **Security**: Attributes are HTML-encoded by default. Use `Meta.safe` or the `safe` template filter for raw HTML, but be wary of XSS.
4.  **Static Files**: The JS files are bundled. Modifications to `src/django_unicorn/static/` usually require running `npm run build` (via `just js-build`).
5.  **Root Element**: Components must have a single root element that is a valid wrapper (non-void element, e.g. `<div>`, `<span>`, `<section>`, etc.). Void elements like `<input>` cannot be the root.

## Useful Resources

- **Official Docs**: `docs/` folder or [django-unicorn.com](https://www.django-unicorn.com).
- **Contributing**: `CONTRIBUTING.md` and `DEVELOPING.md` for setup instructions.
- **Example App**: `example/` directory contains many practical examples of components.
