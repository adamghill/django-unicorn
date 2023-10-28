# JavaScript Integration

## Call JavaScript from View

To integrate with other JavaScript functions, view methods can call an arbitrary JavaScript function after it gets rendered.

```html
<!-- call-javascript.html -->
<div>
  <script>
    function hello(name) {
      alert("Hello, " + name);
    }
  </script>

  <input type="text" unicorn:model="name" />
  <button type="submit" unicorn:click="hello">Hello!</button>
</div>
```

```python
# call_javascript.py
from django_unicorn.components import UnicornView

class CallJavascriptView(UnicornView):
    name = ""

    def mount(self):
        self.call("hello", "world")

    def hello(self):
        self.call("hello", self.name)
```

## Trigger Model Update

Normally when a model element gets changed by a user it will trigger an event which `Unicorn` listens for (either `input` or `blur` depending on if it has a `lazy` modifier). However, when setting an element with JavaScript those events do not fire. `Unicorn.trigger()` provides a way to trigger that event from JavaScript manually.

The first argument to `trigger` is the component name. The second argument is the value for the element's `unicorn:key`.

```html
<!-- trigger-model.html -->
<input
  id="nameId"
  unicorn:key="nameKey"
  unicorn:model="name"
  value="initial value"
/>

<script>
  document.getElementById("nameId").value = "new value";
  Unicorn.trigger("hello_world", "nameKey");
</script>
```
