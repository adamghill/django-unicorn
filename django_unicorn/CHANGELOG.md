# Changelog

## v0.30.0

- Look in all `INSTALLED_APPS` for components instead of only in a `unicorn` app [210](https://github.com/adamghill/django-unicorn/issues/210)
- Support `settings.APPS_DIR` which is the default for `django-cookiecutter` instead of just `settings.BASE_DIR` [214](https://github.com/adamghill/django-unicorn/issues/214)

** Breaking changes **

- Require an application name when running the `startunicorn` management command for where the component should be created

[All changes since 0.29.0](https://github.com/adamghill/django-unicorn/compare/0.29.0...0.30.0).

## v0.29.0

- Sanitize initial JSON to prevent XSS

[All changes since 0.28.0](https://github.com/adamghill/django-unicorn/compare/0.28.0...0.29.0).

## v0.28.0

- Re-fire poll method when tab/window comes back into focus after losing visibility (https://github.com/adamghill/django-unicorn/pull/202 by [frbor](https://github.com/frbor))

[All changes since 0.27.2](https://github.com/adamghill/django-unicorn/compare/0.27.2...0.28.0).

## v0.27.2

- Fix bug with relationship fields on a Django model

[All changes since 0.27.1](https://github.com/adamghill/django-unicorn/compare/0.27.1...0.27.2).

## v0.27.1

- Fix some issues with many-to-many fields on a Django model

[All changes since 0.27.0](https://github.com/adamghill/django-unicorn/compare/0.27.0...0.27.1).

## v0.27.0

- Many-to-many fields on a Django model are now supported
- Multiple partial targets

[All changes since 0.26.0](https://github.com/adamghill/django-unicorn/compare/0.26.0...0.27.0).

## v0.26.0

- Completely redesigned and much improved support for [Django models and QuerySets](https://www.django-unicorn.com/docs/django-models/).
- Fix the `startunicorn` command and add some ascii art.

[All changes since 0.25.0](https://github.com/adamghill/django-unicorn/compare/0.25.0...0.26.0).

## v0.25.0

- Support calling functions in JavaScript modules.
- Fix: use `unicorn:db` without a `unicorn:model` in the same element.

[All changes since 0.24.0](https://github.com/adamghill/django-unicorn/compare/0.24.0...0.25.0).

## v0.24.0

- Support custom CSRF headers set with [CSRF_HEADER_NAME](https://docs.djangoproject.com/en/stable/ref/settings/#csrf-header-name) setting.

[All changes since 0.23.0](https://github.com/adamghill/django-unicorn/compare/0.23.0...0.24.0).

## v0.23.0

- Performance enhancement that returns a 304 HTTP status code when an action happens, but the content doesn't change.
- Add [`unicorn:ignore`](https://www.django-unicorn/docs/templates/#ignore-elements) attribute to prevent an element from being morphed (useful when using `Unicorn` with libraries like `Select2` that change the DOM).
- Add support for passing arguments to [`Unicorn.call`](https://www.django-unicorn.com/docs/actions/#calling-methods).
- Bug fix when attempting to cache component views that utilize the `db_model` decorator.

[All changes since 0.22.0](https://github.com/adamghill/django-unicorn/compare/0.22.0...0.23.0).

## v0.22.0

- Use Django cache for storing component state when available
- Add support for Django 2.2.x

[All changes since 0.21.2](https://github.com/adamghill/django-unicorn/compare/0.21.2...0.22.0).

## v0.21.2

- Add backported `dataclasses` for Python 3.6. ([@frbor](https://github.com/frbor))

[All changes since 0.21.0](https://github.com/adamghill/django-unicorn/compare/0.21.0...0.21.2).

## v0.21.0

- Bug fix: Prevent disabled polls from firing at all.
- Support [`Decimal` field type](https://www.django-unicorn.com/docs/components/#supported-property-types).
- Support [`dataclass` field type](https://www.django-unicorn.com/docs/components/#supported-property-types).
- Use [type hints](https://www.django-unicorn.com/docs/components/#property-type-hints) to cast fields to primitive Python types if possible.

[All changes since 0.20.0](https://github.com/adamghill/django-unicorn/compare/0.20.0...0.21.0).

## v0.20.0

- Add ability to exclude component view properties from JavaScript to reduce the amount of data initially rendered to the page with [`javascript_exclude`](https://www.django-unicorn.com/docs/advanced/#javascript_exclude).
- Add [`complete`](https://www.django-unicorn.com/docs/advanced/#complete), [`rendered`](https://www.django-unicorn.com/docs/advanced/#renderedhtml), [`parent_rendered`](https://www.django-unicorn.com/docs/advanced/#parent_renderedhtml) component hooks.
- Call [JavaScript functions](https://www.django-unicorn.com/docs/advanced/#javascript-integration) from a component view's method.

[All changes since 0.19.0](https://github.com/adamghill/django-unicorn/compare/0.19.0...0.20.0).

## v0.19.0

- Re-implemented how action method parsing is done to remove all edge cases when passing arguments to component view methods. ([@frbor](https://github.com/frbor)).
- Add support for passing kwargs to component view methods.

[All changes since 0.18.1](https://github.com/adamghill/django-unicorn/compare/0.18.1...0.19.0).

## v0.18.1

- Fix regression where component kwargs were getting lost (<a href="https://github.com/adamghill/django-unicorn/issues/140">#140</a>, <a href="https://github.com/adamghill/django-unicorn/issues/141">#141</a>)
- Fix <code>startunicorn</code> management command (<a href="https://github.com/adamghill/django-unicorn/issues/142">#142</a>)

[All changes since 0.18.0](https://github.com/adamghill/django-unicorn/compare/0.18.0...0.18.1).

## v0.18.0

- Only send updated data back in the response to reduce network latency.
- Experimental support for [queuing up requests](https://www.django-unicorn.com/docs/queue-requests/) to alleviate race conditions when functions take a long time to process.
- Bug fix: prevent race condition where an instantiated component class would be inadvertently re-used for component views that are slow to render
- Bug fix: use the correct component name to call a [component method from "outside" the component](https://www.django-unicorn.com/docs/actions/#calling-methods).
- Deprecated: `DJANGO_UNICORN` setting has been renamed to `UNICORN`.

[All changes since 0.17.2](https://github.com/adamghill/django-unicorn/compare/0.17.2...0.18.0).

## v0.17.2

- Don't send the parent context in the response for child components that specify a partial update.
- Add support for element models to specify a partial update.
- Add support for polls to specify a partial update.
- Handle `date`, `time`, `timespan` when passed as arguments from JavaScript.
- Render child component template's JavaScript initialization with the parent's as opposed to inserting a new script tag after the child component is rendered.
- Bug fix: prevent an error when rendering a Django model with a date-related field, but a string value.

[All changes since 0.17.1](https://github.com/adamghill/django-unicorn/compare/0.17.1...0.17.2).

## v0.17.1

- Remove stray print statement.
- Fix bug where child components would sometimes lose their action events.

[All changes since 0.17.0](https://github.com/adamghill/django-unicorn/compare/0.17.0...0.17.1).

## v0.17.0

- Target DOM changes from an action to only a portion of the DOM with [partial updates](https://www.django-unicorn.com/docs/partial-updates/).

[All changes since 0.16.1](https://github.com/adamghill/django-unicorn/compare/0.16.1...0.17.0).

## v0.16.1

- Remove debounce from action methods to reduce any perceived lag.

[All changes since 0.16.0](https://github.com/adamghill/django-unicorn/compare/0.16.0...0.16.1).

## v0.16.0

- [Dirty states](https://www.django-unicorn.com/docs/dirty-states/) for when there is a change that hasn't been synced yet.
- Add support for setting [multiple classes for loading states](https://www.django-unicorn.com/docs/loading-states/#class).
- Attempt to handle when the component gets out of sync with an invalid checksum error.
- Performance tweaks when there isn't a change to a model or dbModel with lazy or defer modifiers.

[All changes since 0.15.1](https://github.com/adamghill/django-unicorn/compare/0.15.1...0.16.0).

## v0.15.1

- Fix bug where a component name has a dash in its name

[All changes since 0.15.1](https://github.com/adamghill/django-unicorn/compare/0.15.0...0.15.1).

## v0.15.0

- Add support for [child components](https://www.django-unicorn.com/docs/child-components/)
- Add [discard](https://www.django-unicorn.com/docs/actions/#discard) action modifier
- Add support for referring to components in a folder structure
- Remove restriction that component templates must start with a div
- Remove restriction that component root can't also have `unicorn:model` or `unicorn:action`

[All changes since 0.15.0](https://github.com/adamghill/django-unicorn/compare/0.14.1...0.15.0).

## v0.14.1

- Prevent the currently focused model element from updating after the AJAX request finishes ([#100](https://github.com/adamghill/django-unicorn/issues/100)).

[All changes since 0.14.0](https://github.com/adamghill/django-unicorn/compare/0.14.0...0.14.1).

## v0.14.0

- [Disable poll](https://www.django-unicorn.com/docs/polling/#disable-poll) with a component field
- Dynamically change polling options with [PollUpdate](https://www.django-unicorn.com/docs/polling/#pollupdate)
- Basic support for [`pydantic`](https://pydantic-docs.helpmanual.io) models

[All changes since 0.13.0](https://github.com/adamghill/django-unicorn/compare/0.13.0...0.14.0).

## v0.13.0

- [Component key](https://www.django-unicorn.com/docs/components/#component-key) to allow disambiguation of components of the same name
- [`$returnValue`](https://www.django-unicorn.com/docs/actions/#returnvalue) special argument
- Get the last action method's [return value](https://www.django-unicorn.com/docs/actions/#return-values)

[All changes since 0.12.0](https://github.com/adamghill/django-unicorn/compare/0.12.0...0.13.0).

## v0.12.0

- [Redirect](https://www.django-unicorn.com/docs/redirecting/) from action method in component

[All changes since 0.11.2](https://github.com/adamghill/django-unicorn/compare/0.11.2...0.12.0).

## v0.11.2

- Fix encoding issue with default component template on Windows ([#91](https://github.com/adamghill/django-unicorn/issues/91))
- Fix circular import when creating the component ([#92](https://github.com/adamghill/django-unicorn/issues/92))

[All changes since 0.11.0](https://github.com/adamghill/django-unicorn/compare/0.11.0...0.11.2).

## v0.11.0

- [`$toggle`](https://www.django-unicorn.com/docs/actions/#toggle) special method.
- Support nested properties when using the [set shortcut](https://www.django-unicorn.com/docs/actions/#set-shortcut).
- Fix action string arguments that would get spaces removed inadvertently.

**Breaking changes**

- All existing special methods now start with a `$` to signify they are magical. Therefore, `refresh` is now [`$refresh`](https://www.django-unicorn.com/docs/actions/#refresh), `reset` is now [`$reset`](https://www.django-unicorn.com/docs/actions/#reset), and `validate` is now [`$validate`](https://www.django-unicorn.com/docs/actions/#validate).

[All changes since 0.10.1](https://github.com/adamghill/django-unicorn/compare/0.10.1...0.11.0).

## v0.10.1

- Use LRU cache for constructed components to prevent ever-expanding memory.
- Loosen `beautifulsoup4` version requirement.
- Fix bug to handle floats so that they don't lose precision when serialized to JSON.
- Fix bug to handle related models (ForeignKeys, OneToOne, etc) fields in Django models.

[All changes since 0.10.0](https://github.com/adamghill/django-unicorn/compare/0.10.0...0.10.1).

## v0.10.0

- Add support for [passing kwargs](https://www.django-unicorn.com/docs/components/#component-arguments) into the component on the template
- Provide access to the [current request](https://www.django-unicorn.com/docs/advanced/#request) in the component's methods

[All changes since 0.9.4](https://github.com/adamghill/django-unicorn/compare/0.9.4...0.10.0).

## v0.9.4

- Fix: Prevent Django `CharField` form field from stripping whitespaces when used for validation.
- Fix: Handle edge case that would generate a null exception.
- Fix: Only change loading state when an action method gets called, not on every event fire.

[All changes since 0.9.1](https://github.com/adamghill/django-unicorn/compare/0.9.1...0.9.3).

## v0.9.3

- Handle child elements triggering an event which should be handled by a parent unicorn element.

[All changes since 0.9.1](https://github.com/adamghill/django-unicorn/compare/0.9.1...0.9.3).

## v0.9.1

- Fix: certain actions weren't triggering model values to get set correctly

[All changes since 0.9.0](https://github.com/adamghill/django-unicorn/compare/0.9.0...0.9.1).

## v0.9.0

- [Loading states](https://www.django-unicorn.com/docs/loading-states/) for improved UX.
- `$event` [special argument](https://www.django-unicorn.com/docs/actions/#events) for `actions`.
- `u` [unicorn attribute](https://www.django-unicorn.com/docs/components/#unicorn-attributes).
- `APPS` [setting](https://www.django-unicorn.com/docs/settings/#apps) for determing where to look for components.
- Add support for parent elements for non-db models.
- Fix: Handle if `Meta` doesn't exist for db models.

[All changes since 0.8.0](https://github.com/adamghill/django-unicorn/compare/0.8.0...0.9.0).

## v0.8.0

- Add much more elaborate support for dealing with [Django models](https://www.django-unicorn.com/docs/django-models/).

[All changes since 0.7.1](https://github.com/adamghill/django-unicorn/compare/0.7.1...0.8.0).

## v0.7.1

- Fix bug where multiple actions would trigger multiple payloads.
- Handle lazy models that are children of an action model better.

[All changes since 0.7.0](https://github.com/adamghill/django-unicorn/compare/0.7.0...0.7.1).

## v0.7.0

- Parse [action method arguments](https://www.django-unicorn.com/docs/actions/#passing-arguments) as basic Python objects
- [Stop and prevent modifiers](https://www.django-unicorn.com/docs/actions/#modifiers) on actions
- [Defer modifier](https://www.django-unicorn.com/docs/templates/#defer) on model
- Support for multiple actions on the same element
- Django setting for whether the JavaScript is [minified](https://www.django-unicorn.com/docs/settings/#minified)

**Breaking changes**

- Remove unused `unicorn_styles` template tag
- Use dash for poll timing instead of dot

[All changes since 0.6.5](https://github.com/adamghill/django-unicorn/compare/0.6.5...0.7.0).

## v0.6.5

- Attempt to get the CSRF token from the cookie first before looking at the CSRF token.

[All changes since 0.6.4](https://github.com/adamghill/django-unicorn/compare/0.6.4...0.6.5).

## v0.6.4

- Fix bug where lazy models weren't sending values before an action was called
- Add `is_valid` method to component to more easily check if a component has validation errors.
- Better error message if the CSRF token is not available.

[All changes since 0.6.3](https://github.com/adamghill/django-unicorn/compare/0.6.3...0.6.4).

## v0.6.3

- Fix bug where model elements weren't getting updated values when an action was being called during the same component update.
- Fix bug where some action event listeners were duplicated.

[All changes since 0.6.2](https://github.com/adamghill/django-unicorn/compare/0.6.2...0.6.3).

## v0.6.2

- More robust fix for de-duping multiple actions.
- Fix bug where conditionally added actions didn't get an event listener.

[All changes since 0.6.1](https://github.com/adamghill/django-unicorn/compare/0.6.1...0.6.2).

## v0.6.1

- Fix model sync getting lost when there is an action ([issue 39](https://github.com/adamghill/django-unicorn/issues/39)).
- Small fix for validations.

[All changes since 0.6.0](https://github.com/adamghill/django-unicorn/compare/0.6.0...0.6.1).

## v0.6.0

- [Realtime validation](https://www.django-unicorn.com/docs/validation/) of a Unicorn model.
- [Polling](https://www.django-unicorn.com/docs/polling/) for component updates.
- [More component hooks](https://www.django-unicorn.com/docs/advanced/)

[All changes since 0.5.0](https://github.com/adamghill/django-unicorn/compare/0.5.0...0.6.0).

## v0.5.0

- [Call](https://www.django-unicorn.com/docs/actions/#calling-methods) component method from JavaScript.
- Support classes, dictionaries, Django Models, (read-only) Django QuerySets properties on a component.
- [Debounce](https://www.django-unicorn.com/docs/templates/#debounce) modifier to change how fast changes are sent to the backend from `unicorn:model`.
- [Lazy](https://www.django-unicorn.com/docs/templates/#lazy) modifier to listen for `blur` instead of `input` on `unicorn:model`.
- Better support for `textarea` HTML element.

[All changes since 0.4.0](https://github.com/adamghill/django-unicorn/compare/0.4.0...0.5.0).

## v0.4.0

- [Set shortcut](https://www.django-unicorn.com/docs/actions/#set-shortcut) for setting properties.
- Listen for any valid event, not just `click`.
- Better handling for model updates when element ids aren't unique.

[All changes since 0.3.0](https://github.com/adamghill/django-unicorn/compare/0.3.0...0.4.0).

## v0.3.0

- Add [mount hook](https://www.django-unicorn.com/docs/advanced/#mount).
- Add [reset](https://www.django-unicorn.com/docs/actions/#reset) action.
- Remove lag when typing fast in a text input and overall improved performance.
- Better error handling for exceptional cases.

[All changes since 0.2.3](https://github.com/adamghill/django-unicorn/compare/0.2.3...0.3.0).

## v0.2.3

- Fix for creating default folders when running `startunicorn`.

[All changes since 0.2.2](https://github.com/adamghill/django-unicorn/compare/0.2.2...0.2.3).

## v0.2.2

- Set default `template_name` if it's missing in component.

[All changes since 0.2.1](https://github.com/adamghill/django-unicorn/compare/0.2.1...0.2.2).

## v0.2.1

- Fix `startunicorn` Django management command.

[All changes since 0.2.0](https://github.com/adamghill/django-unicorn/compare/0.2.0...0.2.1).

## v0.2.0

- Switch from `Component` class to `UnicornView` to follow the conventions of class-based views.
- [Investigate using class-based view instead of the custom Component class](https://github.com/adamghill/django-unicorn/issues/4)

[All changes since 0.1.1](https://github.com/adamghill/django-unicorn/compare/0.1.1...0.2.0).

## v0.1.1

- Fix package readme and repository link.

[All changes since 0.1.0](https://github.com/adamghill/django-unicorn/compare/0.1.0...0.1.1).

## v0.1.0

- Initial version with basic functionality.
