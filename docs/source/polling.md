# Polling

`unicorn:poll` can be added to the root `div` element of a component to have it refresh the component automatically every 2 seconds. The polling is smart enough that it won't poll when the page is inactive.

```python
# polling.py
from django.utils.timezone import now
from django_unicorn.components import UnicornView

class PollingView(UnicornView):
    current_time = now()
```

```html
<!-- polling.html -->
<div unicorn:poll>{{ current_time }}</div>
```

A method can also be specified if there is a specific method on the component that should called every time the polling fires. For example, `unicorn:poll="get_updates"` would call the `get_updates` method instead of the built-in `refresh` method.

To define a different refresh time in milliseconds, a modifier can be added as well. `unicorn:poll-1000` would fire the `refresh` method every 1 second, instead of the default 2 seconds.

```html
<!-- polling-every-five-seconds.html -->
<div unicorn:poll-5000="get_updates">
  <input unicorn:model="update" type="text" id="text" />
  {{ update }}
</div>
```

## Disable poll

Polling can dynamically be disabled by checking a boolean field from the component.

```python
# poll_disable.py
from django.utils.timezone import now
from django_unicorn.components import UnicornView

class PollDisableView(UnicornView):
    polling_disabled = False
    current_time = now()

    def get_date(self):
        self.current_time = now()
```

:::{code} html
:force:

<!-- poll-disable.html -->
<div unicorn:poll-1000="get_date" unicorn:poll.disable="polling_disabled">
    current_time: {{ current_time|date:"s" }}<br />
    <button u:click="$toggle('polling_disabled')">Toggle Polling</button>
</div>
:::

````{note}
The field passed into `unicorn:poll.disable` can be negated with an exclamation point.

```python
# poll_disable_negation.py
from django.utils.timezone import now
from django_unicorn.components import UnicornView

class PollDisableNegationView(UnicornView):
    polling_enabled = True
    current_time = now()

    def get_date(self):
        self.current_time = now()
```

:::{code} html
:force:

<!-- poll-disable-negation.html -->
<div unicorn:poll-1000="get_date" unicorn:poll.disable="!polling_enabled">
    current_time: {{ current_time|date:"s" }}<br />
    <button u:click="$toggle('polling_enabled')">Toggle Polling</button>
</div>
:::
````

## PollUpdate

A poll can be dynamically updated by returning a `PollUpdate` object from an action method. The timing and method can be updated, or it can be disabled.

```python
# poll_update.py
from django.utils.timezone import now
from django_unicorn.components import PollUpdate, UnicornView

class PollingUpdateView(UnicornView):
    polling_disabled = False
    current_time = now()

    def get_date(self):
        self.current_time = now()
        return PollUpdate(timing=2000, disable=False, method="get_date")
```

:::{code} html
:force:

<!-- poll-update.html -->
<div unicorn:poll-1000="get_date">
    current_time: {{ current_time|date:"s" }}<br />
</div>
:::
