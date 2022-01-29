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

:::

```python
# messages.py
from django.contrib import messages
from django_unicorn.components import UnicornView

class MessagesView(UnicornView):
    def update(self):
        messages.success(self.request, "update called")
```
