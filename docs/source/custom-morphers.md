# Custom Morphers

Morpher is a library used to update specific parts of the DOM element instead of replacing the entire element. This improves performance and maintains the state of unchanged DOM elements, such as the cursor position in an input.

The default morpher used in Unicorn is [morphdom](https://github.com/patrick-steele-idem/morphdom). If you don't change any settings, morphdom will be used. However, you can switch to a different morpher by setting the "MORPHER" parameter. Each morpher has its own set of configurable settings, which can be adjusted using the "MORPHER_OPTIONS" parameter in the "UNICORN" setting.

Currently, the only alternative morpher available is the [Alpine.js Morph Plugin](https://alpinejs.dev/plugins/morph).

## Morphdom

Since it's the default morpher, and it's built into Unicorn, no extra steps are required to use it.

### Morphdom Settings

```python
# File: settings.py

UNICORN = {
    "MORPHER": "morphdom",
    "MORHER_OPTIONS": {
        "RELOAD_SCRIPT_ELEMENTS": False,
    },
}
```

### Morphdom Options

- **RELOAD_SCRIPT_ELEMENTS** (default is `False`): Whether `script` elements in a template should be "re-run" after a template has been re-rendered.

## Alpine

The Alpine morpher is helpful if you use Alpine.js and need to keep the Alpine state of your components after a template has been re-rendered.


### Alpine Options

The Alpine.js morpher doesn't have any options.

### Alpine Installation

To use the Alpine.js morpher, you need to include Alpine.js and Alpine.js Morpher plugin in your template. You can do this by adding the following line to your template:

```html
<head>
  ...
  <script defer src="https://unpkg.com/@alpinejs/morph@3.x.x/dist/cdn.min.js"></script>
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
  {% unicorn_scripts %}
</head>
```

Then switch to the Alpine.js morpher in your settings:

```python
# File: settings.py

UNICORN = {
    "MORPHER": "alpine",
}
```
