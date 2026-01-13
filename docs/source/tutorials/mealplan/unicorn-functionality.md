# Django Unicorn Concepts

## Setup

Django Unicorn uses the term "[Component](../../components.md)" to refer to a set (or a block) of interactive functionality. Similar to how your Django _views_ connect to your _templates_, `Unicorn` uses a special [view class](../../views.md) (`UnicornView`) residing within a special `components` directory linking to a specific _template_ with the _same name_ as the `component` module.

Phew. That's a lot of words. Perhaps it's easier if you see it.

While you can create the directory structure manually, Django Unicorn also includes a special command that will do this for you. 

In your terminal, type the following command:

```shell
python manage.py startunicorn mealplan create-meal
```

This command tells unicorn to create a component/template combo in your `mealplan` app, with the name of `create-meal.py` and `create-meal.html` respectively.

After you successfully run the command, your file structure will look like this:

```
mealplan/  
┣ components/           # New!
┃ ┣ create_meal.py      # New!
┃ ┗ __init__.py         # New!
┣ migrations/  
┣ templates/  
┃ ┣ mealplan/  
┃ ┃ ┗ meals.html  
┃ ┗ unicorn/            # New!
┃   ┗ create-meal.html  # New!
┣ admin.py
┣ apps.py  
┣ forms.py  
┣ models.py  
┣ tests.py  
┣ urls.py  
┣ views.py  
┗ __init__.py
```

You could create those files marked as `# New!` manually, but the command makes it easy for you.

If you build additional components, you would create new files in the `components` directory as well as in the `template/unicorn`directory with the same name (note the distinction between the `.py` and `.html` extensions, as well as the hyphen and underscore).

In order to use components within your regular Django templates, you need to "include" them within your HTML file.

Let's go back to `index.html` and add it at the very top of the file.

:::{code} html
:force: true
<!-- mealplan/templates/mealplan/meals.html -->

{% load unicorn %}   
<!DOCTYPE html>
<html lang="en">
...
:::

There are two more items that you need to add to your templates to ensure Django Unicorn functions properly. The first is a `{% unicorn_scripts %}` tag. You can place that in the `<head>` element in your HTML.

:::{code} html
:force: true
<!-- mealplan/templates/mealplan/meals.html -->

...
<head>
    <title>Meal Plan</title>
    <link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
    {% unicorn_scripts %}
</head>
...
:::

And secondly, a `{% csrf_token %}` tag within the body of your HTML. We can include it near the end.

:::{code} html
:force: true
<!-- mealplan/templates/mealplan/meals.html -->
 
...
    </footer>
    {% csrf_token %}
</body>
</html>
:::

```{note}
In case you missed it earlier and if you haven't already done so, make sure that `django_unicorn` is listed within your `INSTALLED_APPS` in your `settings.py` file.
```

## Components

Components are where much of the Django Unicorn heavy lifting occurs. Here, we will define a `UnicornView`, which in turn contains the back end logic which will be passed to the corresponding `template`.

The interaction between the component and the template is unique to this pairing, and it is "included" in your Django templates with a special template tag. The tag contains the name `unicorn`, followed by the name of the template, which in turn corresponds to the matching component.

For example, to load the component we created earlier, we would add this template tag to our `meal.html` template. (Here, it is included within then `<div>` element).

:::{code} html
:force: true
<!-- mealplan/templates/mealplan/meals.html -->

...
<body>
    <main class="container">
        <header>
            <h1>Meal Plan</h1>
        </header>
        <div>
            {% unicorn "create-meal" %}
            <hr />
        </div>
        <footer>
            <p>2024 &copy;</p>
            <p><a href="/admin">Admin</a></p>
        </footer>
        {% csrf_token %}
    </main>
</body>
...
:::

Now we can define what actually goes in the `create-meal.html` template.

:::{code} html
:force: true
<!-- mealplan/templates/unicorn/create-meal.html -->

{% load unicorn %}
<div>
    <div unicorn:model = "meals">
        {% if not meals %}
            <p>No meals yet</p>
        {% else %}
        {% for meal in meals %}
            <p>{{ meal.name }}</p>
        {% endfor %}
        {% endif %}
    </div>
</div>
:::

Notice the `unicorn:model` attribute on the `<div>` element. This is what "binds" this element to the logic we will write next in the `create_meal.py` component.

```{warning}
The term `model` in this particular context _does not_ correlate to a Django `Model`. In other words, `unicorn:model` is what enables reactivity. Django Unicorn holds the fields from the component (`create_model.py`) in a special context. Then, when the element with `unicorn:model` triggers a change (whether on load, click, submit, blur, etc...), then it sends an AJAX request to a specific Unicorn endpoint, and the response is rendered in place. You don't necessarily have to understand all of that, but it's worth noting that `unicorn:model` is _not_ referring to your Django `Model` directly.
```

Our last piece here is to actually write some logic in the component.

In our `create_meal.py` file, we will create a `UnicornView` which will handle our backend logic.

If you noticed in our template code above, we want to check to see if we have any "Meals" in the database. If none are found, we want to display a message stating as so. However, if we do find any meals, we want to iterate through them and list the `name` of that meal.

So in our component, we will defined a "field" corresponding to a list of Meals in our database.

```python
# mealplan/components/create_meal.py

from django_unicorn.components import UnicornView
from mealplan.models import Meal

class CreateMealView(UnicornView):
    meals: list[Meal] = None

    def mount(self):
        self.meals = Meal.objects.all()

```

The name of your view should match the name of your component (but in CamelCase). We're defining a field called `meals` which will correspond to any meals we are able to load from the database. Lastly, we define the `mount` method. This method will get called when the component gets initialized or reset.

Since we don't currently have any Meals in the database, this may not seem like it is doing much.

Let's add some cool functionality.