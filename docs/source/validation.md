# Validation

`Unicorn` uses Django `forms` infrastructure for all validation. This means that a form could be re-used between any other Django views and a `Unicorn`.

Using the Django `forms` system provides a way to serialize/deserialize certain classes (for example, `datetime` and `uuid`) and a way to validate properties of a class.

```{note}
There are many [built-in fields available for Django form fields](https://docs.djangoproject.com/en/stable/ref/forms/fields/#built-in-field-classes) which can be used to validate text inputs.
```

```python
# book.py
from django_unicorn.components import UnicornView
from django import forms

class BookForm(forms.Form):
    title = forms.CharField(max_length=100, required=True)
    publish_date = forms.DateField(required=True)

class BookView(UnicornView):
    form_class = BookForm

    title = ""
    publish_date = ""
```

```html
<!-- book.html -->
<div>
  <input unicorn:model="title" type="text" id="title" /><br />
  <input unicorn:model="publish_date" type="text" id="publish-date" /><br />
  <button unicorn:click="$validate">Validate</button>
</div>
```

Because of the `form_class = BookForm` defined on the `UnicornView` above, `Unicorn` will automatically validate that the title has a value and is less than 100 characters. The `publish_date` will also be converted into a `datetime` from the string representation in the text input.

## Showing validation errors

As the form is filled out the appropriate inputs will be validated. There are a few ways to show the validation messages.

### Highlighting the invalid form

When a model form is invalid, a special `unicorn:error` attribute is added to the element. Depending on whether it is an `invalid` or `required` error code, the attribute will be `unicorn:error:invalid` or `unicorn:error:required`. The value of the attribute will be the validation message.

:::{code} html
:force: true

<!-- highlight-input-errors.html -->
<div>
  <style>
    [unicorn\:error\:invalid] {
      border: 1px solid red !important;
    }
    [unicorn\:error\:required] {
      border: 1px solid red !important;
    }
  </style>

<input
  unicorn:model="publish_date"
  type="text"
  id="publish-date"
  unicorn:error:invalid="Enter a valid date/time."
/><br />

</div>
:::

### Showing a specific error message

```html
<!-- show-error-message.html -->
<div>
  <input unicorn:model="publish_date" type="text" id="publish-date" /><br />
  <span class="error">{{ unicorn.errors.publish_date.0.message }}</span>
</div>
```

### Showing all the error messages

There is a `unicorn_errors` template tag that shows all errors for the component. It should provide an example of how to display component errors in a more specific way if needed.

```html
<!-- show-all-error-messages.html -->
{% load unicorn %}

<div>
  {% unicorn_errors %}

  <input unicorn:model="publish_date" type="text" id="publish-date" /><br />
</div>
```

## Validate the entire component

The magic action method `$validate` can be used to validate the whole component by the front-end.

```html
<!-- validate.html -->
<div>
  <input unicorn:model="publish_date" type="text" id="publish-date" /><br />
  <button unicorn:click="$validate">Validate</button>
</div>
```

The `validate` method can also be used inside of the component.

```python
# validate.py
from django_unicorn.components import UnicornView
from django import forms

class BookForm(forms.Form):
    title = forms.CharField(max_length=6, required=True)

class BookView(UnicornView):
    form_class = BookForm

    text = "hello"

    def set_text(self):
        self.text = "hello world"
        self.validate()
```

The `is_valid` can also be used inside of the component to check if a component is valid.

```python
# validate.py
from django_unicorn.components import UnicornView
from django import forms

class BookForm(forms.Form):
    title = forms.CharField(max_length=6, required=True)

class BookView(UnicornView):
    form_class = BookForm

    text = "hello"

    def set_text(self):
        if self.is_valid():
            self.text = "hello world"
```
