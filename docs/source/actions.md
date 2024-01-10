# Actions

Components can also trigger methods from the templates by listening to any valid event type. The most common events would be `click`, `input`, `keydown`, `keyup`, and `mouseenter`, but [MDN has a list of all of the browser event types available](https://developer.mozilla.org/en-US/docs/Web/Events).

## Events

An example action to call the `clear_name` method on the component.

```html
<!-- clear-name.html -->
<div>
  <input unicorn:model="name" type="text" id="text" />
  Hello {{ name|title }}
  <button unicorn:click="clear_name">Clear Name</button>
</div>
```

```python
# clear_name.py
from django_unicorn.components import UnicornView

class ClearNameView(UnicornView):
    name = "World"

    def clear_name(self):
        self.name = ""
```

When the button is clicked, the `name` property will get set to an empty string. Then, the component will intelligently re-render itself and the text input will update to match the property on the component.

```{tip}
Instance methods without arguments can be called from the template with or without parenthesis.
```

## Passing arguments

Actions can also pass basic Python types to the backend component.

```html
<!-- passing-args.html -->
<div>
  <input unicorn:model="name" type="text" id="text" />
  Hello {{ name|title }} 👋
  <button unicorn:click="set('Bob')">Set as Bob</button>
  <button unicorn:click="set()">Set default value of name argument</button>
</div>
```

```python
# passing_args.py
from django_unicorn.components import UnicornView

class PassingArgsView(UnicornView):
    name = "World"

    def set(self, name="Universe"):
        self.name = name
```

### Argument types

Most basic Python types, including `string`, `int`, `float`, `bool`, `list`, `tuple`, `dictionary`, and `set`, are supported by default.

```html
<!-- argument-types.html -->
<div>
  <button unicorn:click="update(99)">Pass int</button>
  <button unicorn:click="update(1.234)">Pass float</button>
  <button unicorn:click="update(True)">Pass bool</button>
  <button unicorn:click="update({'key': 'value'})">Pass dictionary</button>
  <button unicorn:click="update([1, 2, 3])">Pass list</button>
  <button unicorn:click="update((1, 2, 3))">Pass tuple</button>
  <button unicorn:click="update({1, 2, 3})">Pass set</button>
</div>
```

#### Coerced types

Arguments with the types of `datetime`, `date`, `time`, `timedelta`, and `UUID` can be coerced by using a type annotation in the action method.

```{note}
[Django's `dateparse` methods](https://docs.djangoproject.com/en/stable/ref/utils/#module-django.utils.dateparse) are used to convert strings to the date-related type.
```

```{note}
Both integer and float epochs can also be coerced into `datetime` or `date` objects.
```

```python
# argument_type_hints.py
from django_unicorn.components import UnicornView
from datetime import date, datetime
from uuid import UUID

class ArgumentTypeHintsView(UnicornView):
    def is_datetime(self, obj: datetime):
        assert type(obj) is datetime
    
    def is_uuid(self, obj: UUID):
        assert type(obj) is UUID

    def is_date(self, obj: date = None):
        assert type(obj) is date
```

```html
<!-- argument-type-hints.html -->
<div>
  <button unicorn:click="is_datetime('2020-09-12T01:01:01')">Check datetime with string</button>
  <button unicorn:click="is_datetime(1691499534)">Check datetime with epoch</button>
  <button unicorn:click="is_uuid('90144cb9-fc47-476d-b124-d543b0cff091')">Check UUID</button>
  <button unicorn:click="is_date(obj='2020-09-12')">Check date</button>
</div>
```

#### Django models

Django models can be instantiated as an argument or with a `pk` kwarg and a type annotation.

```python
# argument_model.py
from django_unicorn.components import UnicornView
from django.contrib.auth.models import User

class ArgumentModelView(UnicornView):
    def is_user_via_arg(self, obj: User):
        assert type(obj) is User
    
    def is_user_via_kwarg(self, pk: User=None):
        assert type(obj) is User
```

```html
<!-- argument-model.html -->
<div>
  <button unicorn:click="is_user_via_arg(1)">Gets user with pk of 1</button>
  <button unicorn:click="is_user_via_kwarg(pk=2)">Gets user with pk of 2</button>
</div>
```

#### Custom types

Custom objects can also be used as a type annotation and `Unicorn` will attempt to instantiate the object with the value that is passed in as the argument.

```python
# argument_custom_type.py
from django_unicorn.components import UnicornView

class CustomType:
  def __init__(self, custom_type_id: int):
    self.custom_type_id = custom_type_id

class ArgumentCustomTypeView(UnicornView):
    def is_custom_type(self, obj: CustomType):
        assert type(obj) is CustomType
```

```html
<!-- argument-custom-type.html -->
<div>
  <button unicorn:click="is_custom_type(1)">Gets custom type</button>
</div>
```

#### Enums

Enums themselves cannot be passed as an argument, but the enum _value_ can be since that is a Python primitive. Use the enum as a type annotation to coerce the value into the specified enum.

```python
# enum.py
from django_unicorn.components import UnicornView
from enum import Enum

class Color(Enum):
  RED = 1
  GREEN = 2
  BLUE = 3
  PURPLE = 4

class EnumView(UnicornView):
    color = Color.RED
    purple_color = Color.PURPLE

    def set_color(self, color: Color):
      self.color = color
```

```html
<!-- enum.html -->
<div>
  <button unicorn:click="set_color({{ color.BLUE.value }})">Show BLUE (and 3) below when clicked</button>
  <button unicorn:click="set_color(2)">Show GREEN (and 2) below when clicked</button>
  <button unicorn:click="set_color({{ purple_color.value }})">Show PURPLE (and 4) below when clicked</button>

  <br />
  <!-- This will be RED when first rendered, and then will change based on the button clicked above -->
  Color: {{ color }}

  <br />
  <!-- This will be 1 when first rendered, and then will change based on the button clicked above -->
  Color int: {{ color.value }}
</div>
```

## Set shortcut

Actions can also set properties without requiring an explicit method.

```html
<!-- set-shortcut.html -->
<div>
  <input unicorn:model="name" type="text" id="text" />
  Hello {{ name|title }} 👋
  <button unicorn:click="name='Bob'">Set name as Bob</button>
</div>
```

```python
# set_shortcut.py
from django_unicorn.components import UnicornView

class SetShortcutView(UnicornView):
    name = "World"
```

## Modifiers

Similar to models, actions also have modifiers which change how the method gets called.

### prevent

Prevents the default action the browser would use for that element. The same as calling `preventDefault`.

:::{code} html
:force: true

<!-- prevent-modifier.html -->
<div>
  <button unicorn:click.prevent="name='Bob'">Set name as Bob</button>
</div>
:::

### stop

Stops the event from bubbling up the event chain. The same as calling `stopPropagation`.

:::{code} html
:force: true

<!-- stop-modifier.html -->
<div>
    <button unicorn:click.stop="name='Bob'">Set name as Bob</button>
</div>
:::

### discard

Discards any model updates from being saved before calling the specified method on the view. Useful for a cancel button.

:::{code} html
:force: true

<!-- discard-modifier.html -->
<div>
    <input type="text" unicorn:model="name">
    <button unicorn:click.discard="cancel">Cancel</button>
</div>
:::

```python
# discard_modifier.py
from django_unicorn.components import UnicornView

class DiscardModifierView(UnicornView):
    name = None

    def cancel(self):
        pass
```

### debounce

Waits the specified time in milliseconds before calling the specified method.

:::{code} html
:force: true

<!-- debounce-modifier.html -->
<div>
    <input type="text" unicorn:model="name">
    <button unicorn:click.debounce-1000="add_count">Add Count</button>
</div>
:::

## Special arguments

### $event

A reference to the event that triggered the action.

```html
<!-- event.html -->
<div>
    <input type="text" unicorn:change="update($event.target.value.trim())">Update</input>
</div>
```

### $returnValue

A reference to the last return value from an action method.

```html
<!-- returnValue.html -->
<div>
    <input type="text" unicorn:change="update($returnValue.trim())">Update</input>
</div>
```

### $parent

A reference to the parent of the current component.

## Special methods

### $refresh

Refresh and re-render the component from its current state.

```html
<!-- refresh-method.html -->
<div>
  <button unicorn:click="$refresh">Refresh the component</button>
</div>
```

### $reset

Revert the component to its original state.

```html
<!-- reset-method.html -->
<div>
  <button unicorn:click="$reset">Reset the component</button>
</div>
```

### $toggle

Toggle a field on the component. Can only be used for fields that are booleans.

```html
<!-- toggle-method.html -->
<div>
  <button unicorn:click="$toggle('check')">Toggle the check field</button>
</div>
```

```{tip}
Multiple fields can be toggled at the same time by passing in multiple fields at a time: `unicorn:click="$toggle('check', 'another_check', 'a_third_check')"`. Nested properties are also supported: `unicorn:click="$toggle('nested.check')"`.
```

### $validate

Validates the component.

```html
<!-- validate-method.html -->
<div>
  <button unicorn:click="$validate">Validate the component</button>
</div>
```

## Calling methods

Sometimes you need to trigger a method on a component from regular JavaScript. That is possible with `Unicorn.call()`. The first argument is the name (or key) of the component and the second argument is the name of the method to call.

```html
<!-- call-with-component-name.html -->
{% unicorn 'hello-world' %}

<button onclick="Unicorn.call('hello-world', 'set_name');">
  Set the name from outside the component
</button>
```

```html
<!-- call-with-component-key.html -->
{% unicorn 'hello-world' key='hello-universe' %}

<button onclick="Unicorn.call('hello-universe', 'set_name');">
  Set the name from outside the component
</button>
```

Passing arguments to the method call is also supported.

```html
<!-- index.html -->
{% unicorn 'hello-world' %}

<button onclick="Unicorn.call('hello-world', 'set_name', 'World');">
  Set the name to "World" from outside the component
</button>
```

## Return values

To retrieve the last action method's return value, use `Unicorn.getReturnValue()`.

```html
<!-- index.html -->
{% unicorn 'hello-world' %}

<button onclick="alert(Unicorn.getReturnValue('hello-world'));">
  Get the last return value
</button>
```
