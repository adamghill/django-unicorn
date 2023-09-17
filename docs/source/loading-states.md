# Loading States

`Unicorn` requires an AJAX request for any component updates, so it is helpful to provide some context to the user that an action is happening.

## Toggling Elements

Elements with the `unicorn:loading` attribute are only visible when an action is in process.

```html
<!-- loading.html -->
<div>
  <button unicorn:click="update">Update</button>

  <div unicorn:loading>Updating!</div>
</div>
```

When the _Update_ button is clicked, the "Updating!" message will show until the action is complete, and then it will re-hide itself.

```{warning}
Loading elements get shown or removed with the [`hidden`](https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/hidden) attribute. One drawback to this approach is that setting the style `display` property overrides this functionality.
```

You can also hide an element while an action is processed by adding a `remove` modifier.

:::{code} html
:force: true

<!-- loading-remove.html -->
<div>
  <button unicorn:click="update">Update</button>

  <div unicorn:loading.remove>Not currently updating!</div>
</div>
:::

If there are multiple actions that happen in the component, you can show or hide a loading element for a specific action by targeting another element's `id` with `unicorn:target`.

```html
<!-- loading-target-id.html -->
<div>
  <button unicorn:click="update" id="updateId">Update</button>
  <button unicorn:click="delete" id="deleteId">Delete</button>

  <div unicorn:loading unicorn:target="updateId">Updating!</div>
  <div unicorn:loading unicorn:target="deleteId">Deleting!</div>
</div>
```

An element's `unicorn:key` can also be targeted.

```html
<!-- loading-target-key.html -->
<div>
  <button unicorn:click="update" unicorn:key="updateKey">Update</button>
  <button unicorn:click="delete" unicorn:key="deleteKey">Delete</button>

  <div unicorn:loading unicorn:target="updateKey">Updating!</div>
  <div unicorn:loading unicorn:target="deleteKey">Deleting!</div>
</div>
```

```{note}
An asterisk can be used as wildcard to target more than one element at a time.

:::{code} html
:force: true

<!-- loading-target-wildcard-id.html -->
<div>
  <button unicorn:click="update" id="update1Id">Update 1</button>
  <button unicorn:click="update" id="update2Id">Update 2</button>

  <div unicorn:loading unicorn:target="update*Id">Updating!</div>
</div>
:::
```

## Toggling Attributes

Elements with an action event can also include an `unicorn:loading` attribute with either an `attr` or `class` modifier.

### attr

Set the specified attribute on the element that is triggering the action.

This example will disable the _Update_ button when it is clicked and remove the attribute once the action is completed.

:::{code} html
:force: true

<!-- loading-attr.html -->
<div>
  <button unicorn:click="update" unicorn:loading.attr="disabled">Update</button>
</div>
:::

### class

Add the specified class(es) to the element that is triggering the action.

This example will add `loading` and `spinner` classes to the _Update_ button when it is clicked and remove the classes once the action is completed.

:::{code} html
:force: true

<!-- loading-class.html -->
<div>
  <button unicorn:click="update" unicorn:loading.class="loading spinner">Update</button>
</div>
:::

### class.remove

Remove the specified class from the element that is triggering the action.

This example will remove a `active` class from the _Update_ button when it is clicked and add the class back once the action is completed.

:::{code} html
:force: true

<!-- loading-class-remove.html -->
<div>
  <button unicorn:click="update" unicorn:loading.class.remove="active">
    Update
  </button>
</div>
:::
