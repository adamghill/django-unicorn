# Messages

`Unicorn` supports Django messages and they work the same as if the template was rendered server-side. When the `update` action is fired, a success message will be added to the request and will show up inside the component.

:::{code} html
:force: true

<!-- messages.html -->
<div>
    {% if messages %}
    <ul class="messages">
        {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    <button unicorn:click="update">Update</button>

</div>

:::

```python
# messages.py
from django.contrib import messages
from django_unicorn.components import UnicornView

class MessagesView(UnicornView):
    def update(self):
        messages.success(self.request, "update called")
```

## Redirecting

When the action returns a `redirect`, `Unicorn` will defer the messages so they do not get rendered in the component (since the user will never see the re-rendered component). Once the redirect has happened `messages` will be available for rendering by the template as expected.

:::{code} html
:force: true

<!-- messages-when-redirecting.html -->
<div>
    <button unicorn:click="update">Update</button>
</div>

:::

:::{code} html
:force: true

<!-- new-url.html -->

{% if messages %}

<ul class="messages">
    {% for message in messages %}
    <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
    {% endfor %}
</ul>
{% endif %}

:::

```python
# messages_when_redirecting.py
from django.contrib import messages
from django.shortcuts import redirect
from django_unicorn.components import UnicornView

class MessagesWhenRedirectingView(UnicornView):
    def update(self):
        messages.success(self.request, "update called")

        return redirect("new-url")
```
