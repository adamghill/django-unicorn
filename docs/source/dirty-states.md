# Dirty States

`Unicorn` can provide context to the user that some data has been changed and will be updated.

## Toggling Attributes

Elements can include an `unicorn:dirty` attribute with either an `attr` or `class` modifier.

### attr

Set the specified attribute on the element that is changed.

This example will set the input to be readonly when the model is changed. The attribute will be removed once the name is synced or if the input value is changed back to the original value.

:::{code} html
:force: true

<!-- dirty-attr.html -->
<div>
  <input unicorn:model="name" unicorn:dirty.attr="readonly" />
</div>
:::

### class

Add the specified class(es) to the model that is changed.

This example will add _dirty_ and _changing_ classes to the input when the model is changed. The classes will be removed once the model is synced or if the input value is changed back to the original value.

:::{code} html
:force: true

<!-- dirty-class.html -->
<div>
  <input unicorn:model="name" unicorn:dirty.class="dirty changing" />
</div>
:::

### class.remove

Remove the specified class(es) from the model that is changed.

This example will remove the _clean_ class from the input when the model is changed. The class will be added back once the model is synced or if the input value is changed back to the original value.

:::{code} html
:force: true

<!-- dirty-class-remove.html -->
<div>
  <input unicorn:model="name" unicorn:dirty.class.remove="clean" />
</div>
:::
