# Templates

Templates are just normal Django HTML templates, so anything you could normally do in a Django template will still work, including template tags, filters, loops, if statements, etc.

```{warning}
`Unicorn` requires there to be one root element surrounding the component template.
```

```{note}
To reduce the verbosity of templates, `u:` can be used as a shorthand for any attribute that starts with `unicorn:`. All of the examples in the documentation use `unicorn:` to be explicit, but both are supported.
```

## Model modifiers

### Lazy

To prevent updates from happening on _every_ input, you can append a `lazy` modifier to the end of `unicorn:model`. That will only update the component when a `blur` event happens.

:::{code} html
:force: true

<!-- waits-for-blur.html -->
<div>
  <input unicorn:model.lazy="name" type="text" id="name" />
  Hello {{ name|title }}
</div>
:::

### Debounce

The `debounce` modifier configures how long to wait to fire an event. The time is always specified in milliseconds, for example: `unicorn:model.debounce-1000` would wait for 1000 milliseconds (1 second) before firing the message.

:::{code} html
:force: true

<!-- waits-1-second.html -->
<div>
  <input unicorn:model.debounce-1000="name" type="text" id="name" />
  Hello {{ name|title }}
</div>
:::

### Defer

The `defer` modifier will store and save model changes until the next action gets triggered. This is useful to prevent additional network requests until an action is triggered.

:::{code} html
:force: true

<!-- defer.html -->
<div>
  <input unicorn:model.defer="task" type="text" id="task" />
  <button unicorn:click="add">Add task</button>
  <ul>
    {% for task in tasks %}
    <li>{{ task }}</li>
    {% endfor %}
  </ul>
</div>
:::

### Chaining modifiers

`Lazy` and `debounce` modifiers can even be chained together.

:::{code} html
:force: true

<!-- waits-for-blur-and-then-5-seconds.html -->
<div>
  <input unicorn:model.lazy.debounce-5000="name" type="text" id="text" />
  Hello {{ name|title }}
</div>
:::

## Key

### Smooth updates

Setting a unique `id` on elements with `unicorn:model` will prevent changes to an input from being choppy when there are lots of updates in quick succession.

```html
<!-- choppy-updates.html -->
<input type="text" unicorn:model="name"></input>
```

```html
!-- smooth-updates.html -->
<input type="text" id="someFancyId" unicorn:model="name"></input>
```

However, setting the same `id` on two elements with the same `unicorn:model` won't work. The `unicorn:key` attribute can be used to make sure that the elements can be synced as expected.

```html
<!-- missing-updates.html -->
<input type="text" id="someFancyId" unicorn:model="name"></input>
<input type="text" id="someFancyId" unicorn:model="name"></input>
```

```html
<!-- this-should-work.html -->
<input type="text" id="someFancyId" unicorn:model="name"></input>
<input type="text" id="someFancyId" unicorn:model="name" unicorn:key="someFancyKey"></input>
```

### DOM merging

The JavaScript library used to merge changes in the DOM, `morphdom`, uses an element's `id` to intelligently update DOM elements. If it isn't possible to have an `id` attribute on the element, `unicorn:key` will be used if it is available.

## Lifecycle events

`Unicorn` provides events that fire when different parts of the lifecycle occur.

### updated

The `updated` event is fired after the AJAX call finishes and the component is merged with the newly rendered component template. The callback gets called with one argument, `component`, which can be inspected if necessary.

```html
<!-- updated-event.html -->

<script type="application/javascript">
  window.addEventListener("DOMContentLoaded", (event) => {
    Unicorn.addEventListener("updated", (component) =>
      console.log("got updated", component)
    );
  });
</script>
```

## Ignore elements

Some JavaScript libraries will change the DOM (such as `Select2`) after the page renders. That can cause issues for `Unicorn` when trying to merge that DOM with what `Unicorn` _thinks_ the DOM should be. `unicorn:ignore` can be used to prevent `Unicorn` from morphing that element or its children.

```{note}
When the component is initially rendered, normal Django template functionality can be used.
```

```html
<!-- ignored-element.html -->
<div>
  <script src="jquery.min.js"></script>
  <link href="select2.min.css" rel="stylesheet" />
  <script src="select2.min.js"></script>

  <div unicorn:ignore>
    <select
      id="select2-example"
      onchange="Unicorn.call('ignored-element', 'select_state', this.value, this.selectedIndex);"
    >
      {% for state in states %}
      <option value="{{ state }}">{{ state }}</option>
      {% endfor %}
    </select>
  </div>

  <script>
    $(document).ready(function () {
      $("#select2-example").select2();
    });
  </script>
</div>
```

```python
# ignored_element.py
from django_unicorn.components import UnicornView

class JsView(UnicornView):
    states = (
        "Alabama",
        "Alaska",
        "Wisconsin",
        "Wyoming",
    )
    selected_state = ""

    def select_state(self, state_name, selected_idx):
        print("select_state state_name", state_name)
        print("select_state selected_idx", selected_idx)
        self.selected_state = state_name
```
