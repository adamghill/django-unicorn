# Tutorial

This tutorial will cover the basics of using `Unicorn` to build reactive components. We will cover how to bind input fields to properties on your component, how to trigger actions from the frontend, and how to use polling to automatically update your component.

## Inputs

`Unicorn` allows you to bind an input field to a property on your component. When the input field changes, the property on the component will meaningful update.

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    name = "World"
```

```html
<!-- hello-world.html -->
<div>
  <input unicorn:model="name" type="text" id="text" />
  Hello {{ name|title }}
</div>
```

In the example above, the `name` property on the `HelloWorldView` component is bound to the input field using `unicorn:model`. When you type in the input field, the `name` property is updated on the component and the component re-renders with the new value.

## Actions

Actions allow you to trigger methods on your component from the frontend. This is useful for handling button clicks, form submissions, and other events.

```python
# clicked.py
from django_unicorn.components import UnicornView

class ClickedView(UnicornView):
    count = 0

    def add(self):
        self.count += 1
```

```html
<!-- clicked.html -->
<div>
  <button unicorn:click="add">Add</button>
  Count: {{ count }}
</div>
```

In this example, we have a `ClickedView` component with a `count` property and an `add` method. The button in the template has `unicorn:click="add"`, which tells `Unicorn` to call the `add` method on the component when the button is clicked. The component then re-renders with the updated count.

## Polling

Polling allows you to automatically refresh your component at a specified interval. This is useful for real-time updates, such as a chat application or a dashboard.

```python
# polling.py
from django.utils.timezone import now
from django_unicorn.components import UnicornView

class PollingView(UnicornView):
    current_time = now()
```

```html
<!-- polling.html -->
<div unicorn:poll>
    Current time: {{ current_time }}
</div>
```

In the example above, the `unicorn:poll` attribute on the root `div` element tells `Unicorn` to refresh the component every 2 seconds. The `current_time` property is updated on the backend and the component re-renders with the new time.

You can also specify a custom storage method to be called:

```html
<div unicorn:poll="get_updates">
    Current time: {{ current_time }}
</div>
```
