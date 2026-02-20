# Partial Updates

Normally `Unicorn` will send the entire component's rendered HTML on every action to make sure that any changes to the context is reflected on the page. However, to reduce latency and minimize the amount of data that has to be sent over the network, `Unicorn` can only update a portion of the page by utilizing the `unicorn:partial` attribute.

```{note}
By default, `unicorn:partial` will look in the current component's template for an `id` or `unicorn:key`. If an element can't be found with the specified target, the entire component will be morphed like usual.
```

```python
# partial_update.py
from django_unicorn.components import UnicornView

class PartialUpdateView(UnicornView):
    checked = False
```

```html
<!-- partial-update.html -->
<div>
  <span id="checked-id">{{ checked }}</span>
  <button unicorn:click="$toggle('checked')" unicorn:partial="checked-id">
    Toggle checked
  </button>
</div>
```

## Target by id

To only target an element `id` add the `id` modifier to `unicorn:partial`.

:::{code} html
:force: true

<!-- partial-update-id.html -->
<div>
  <span id="checked-id">{{ checked }}</span>
  <button unicorn:click="$toggle('checked')" unicorn:partial.id="checked-id">
    Toggle checked
  </button>
</div>
:::

## Target by key

To only target an element `unicorn:key` add the `key` modifier to `unicorn:partial`.

:::{code} html
:force: true

<!-- partial-update-key.html -->
<div>
  <span unicorn:key="checked-key">{{ checked }}</span>
  <button unicorn:click="$toggle('checked')" unicorn:partial.key="checked-key">
    Toggle checked
  </button>
</div>
:::

```{note}
Multiple partials can be targetted by adding multiple attributes to the element.

:::{code} html
:force: true

<button unicorn:click="$toggle('checked')" unicorn:partial.key="checked-key" unicorn:partial.id="checked-id">
:::

```
