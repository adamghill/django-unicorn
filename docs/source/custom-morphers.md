# Custom Morphers

The morpher is a library used to update specific parts of the DOM element instead of replacing the entire element. This improves performance and maintains the state of unchanged DOM elements, such as the cursor position in an input.

The default morpher used in Unicorn is [`morphdom`](https://github.com/patrick-steele-idem/morphdom). The only alternative morpher available is the [Alpine.js morph plugin](https://alpinejs.dev/plugins/morph).

## `Morphdom`

`morphdom` is the default morpher so no extra settings or installation is required to use it.

## `Alpine`

Components which use both `Unicorn` and `Alpine.js` should use the `Alpine.js` morpher to prevent losing state when it gets re-rendered.

## Django Settings

```python
# settings.py

UNICORN = {
    ...
    "MORPHER": {
        "NAME": "alpine",
    }
    ...
}
```

```{note}
`MORPHER.RELOAD_SCRIPT_ELEMENTS` is not currently supported for the `Alpine.js` morpher.
```

### JavaScript Installation

`Alpine.js` is not included in `Unicorn` so you will need to manually include it. Make sure to include `Alpine.js` and the morpher plugin by adding the following line to your template before `{% unicorn_scripts %}`.

```html
...
<head>
  <script defer src="https://unpkg.com/@alpinejs/morph@3.x.x/dist/cdn.min.js"></script>
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
  {% unicorn_scripts %}
</head>
...
```
