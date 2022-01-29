# Visibility

`unicorn:visible` can be added to any element to have it call the specified view method when it scrolls into view.

```python
# visibility.py
from django_unicorn.components import UnicornView

class VisibilityView(UnicornView):
    visibility_count = 0

    def add_count(self):
        self.visibility_count += 1
```

```html
<!-- visibility.html -->
<div>
    <div style="height: 100%">
        <span unicorn:visible="add_count">
    </div>
</div>
```

```{note}
In some cases, the element with the `unicorn:visible` attribute will always be in the viewport, so the event will continue to fire and the method will continue to execute. However, this will not happen in the following instances:

- the fields of component do not change, so the AJAX request will return a 304 status code
- the method explicitly returns `False`
```

## Modifiers

There are a few modifiers for `unicorn:visible` and they are able to be chained if necessary.

### Debounce

Similar to the debounce modifier on a [model](templates.md#debounce) or [actions](actions.md#debounce), wait the specified number of milliseconds before calling the specified method.

:::{code} html
:force: true

<!-- debounce-modifier.html -->
<div>
    <div style="height: 100%">
        <span unicorn:visible.debounce-1000="add_count"></span>
    </div>
</div>
:::

### Threshold

The percentage (as an integer) that should be visible before being triggered. For example, `0` means that as soon as 1 pixel of the element is visible it would be fired, `25` would be 25% of the target element is visible, `100` would require 100% of the element to be completely visible.

:::{code} html
:force: true

<!-- threshold-modifier.html -->
<div>
    <div style="height: 100%">
        <span unicorn:visible.threshold-25="add_count"></span>
    </div>
</div>
:::
