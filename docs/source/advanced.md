# Advanced Views

## Class properties

### template_name

By default, the component name is used to determine what template should be used. For example, `hello_world.HelloWorldView` would by default use `unicorn/hello-world.html`. However, you can specify a particular template by setting `template_name` in the component.

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    template_name = "unicorn/hello-world.html"
```

## Instance properties

### request

The current `request` is available on `self` in the component's methods.

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    def __init__(self, *args, **kwargs):
        super.__init__(**kwargs)
        print("Initial request that rendered the component", self.request)

    def test(self):
        print("callMethod request to re-render the component", self.request)
```

## Custom methods

Defined component instance methods with no arguments are made available to the Django template context and can be called like a property.

```python
# states.py
from django_unicorn.components import UnicornView

class StateView(UnicornView):
    def all_states(self):
        return ["Alabama", "Alaska", "Arizona", ...]
```

```html
<!-- states.html -->
<div>
  <ul>
    {% for state in all_states %}
    <li>{{ state }}</li>
    {% endfor %}
  </ul>
</div>
{% endverbatim %}
```

:::{tip}
If the method is intensive and will be called multiple times, it can be cached with Django's <a href="https://docs.djangoproject.com/en/stable/ref/utils/#django.utils.functional.cached_property">`cached_property`</a> to prevent duplicate API requests or database queries. The method will only be executed once per component rendering.

```python
# states.py
from django.utils.functional import cached_property
from django_unicorn.components import UnicornView

class StateView(UnicornView):
    @cached_property
    def all_states(self):
        return ["Alabama", "Alaska", "Arizona", ...]
```

:::

## Instance methods

### \_\_init\_\_()

Gets called when the component gets constructed for the very first time. Note that constructed components get cached to reduce the amount of time discovering and instantiating them, so `__init__` only gets called the very first time the component gets rendered.

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    name = "original"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.name = "initialized"
```

### mount()

Gets called when the component gets initialized or [reset](actions.md#reset).

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    name = "original"

    def mount(self):
        self.name = "mounted"
```

### hydrate()

Gets called when the component data gets set.

```python
# hello_world.py
from django_unicorn.components import UnicornView

class HelloWorldView(UnicornView):
    name = "original"

    def hydrate(self):
        self.name = "hydrated"
```

### updating(name, value)

Gets called before each property that will get set.

### updated(name, value)

Gets called after each property gets set.

### updating\_{property_name}(value)

Gets called before the specified property gets set.

### updated\_{property_name}(value)

Gets called after the specified property gets set.

### calling(name, args)

Gets called before each method that gets called.

### called(name, args)

Gets called after each method gets called.

### complete()

Gets called after all methods have been called.

### rendered(html)

Gets called after the component has been rendered.

### parent_rendered(html)

Gets called after the component's parent has been rendered (if applicable).

## Meta

Classes that derive from `UnicornView` can include a `Meta` class that provides some advanced options for the component.

### exclude

By default, all public attributes of the component are included in the context of the Django template and available to JavaScript. One way to protect internal-only data is to prefix the atteibute name with `_` to indicate it should stay private.

```python
# hello_state.py
from django_unicorn.components import UnicornView

class HelloStateView(UnicornView):
    _all_states = (
        "Alabama",
        "Alaska",
        ...
        "Wisconsin",
        "Wyoming",
    )
```

Another way to prevent that data from being available to the component template is to add it to the `Meta` class's `exclude` tuple.

```python
# hello_state.py
from django_unicorn.components import UnicornView

class HelloStateView(UnicornView):
    all_states = (
        "Alabama",
        "Alaska",
        ...
        "Wisconsin",
        "Wyoming",
    )

    class Meta:
        exclude = ("all_states", )
```

### javascript_exclude

To allow an attribute to be included in the the context to be used by a Django template, but not exposed to JavaScript, add it to the `Meta` class's `javascript_exclude` tuple.

```html
<!-- hello-state.html -->
<div>
  {% for state in all_states %}
  <div>{{ state }}</div>
  {% endfor %}
</div>
```

```python
# hello_state.py
from django_unicorn.components import UnicornView

class HelloStateView(UnicornView):
    all_states = (
        "Alabama",
        "Alaska",
        ...
        "Wisconsin",
        "Wyoming",
    )

    class Meta:
        javascript_exclude = ("all_states", )
```

### safe

By default, `unicorn` HTML encodes updated field values to prevent XSS attacks. You need to explicitly opt-in to allow a field to be returned without being encoded by adding it to the `Meta` class's `safe` tuple.

```html
<!-- safe-example.html -->
<div>
  <input unicorn:model="something_safe" />
  {{ something_safe }}
</div>
```

```python
# safe_example.py
from django_unicorn.components import UnicornView

class SafeExampleView(UnicornView):
    something_safe = ""

    class Meta:
        safe = ("something_safe", )
```

````{note}
A context variable can be marked as `safe` in the template with the normal Django template filter, as well.

```html
<!-- safe-example.html -->
<div>
  <input unicorn:model="something_safe" />
  {{ something_safe|safe }}
</div>
```
````

## JavaScript Integration

### Call JavaScript from View

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

### Trigger Model Update

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
