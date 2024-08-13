(beginner-tutorial)=
# Beginner Tutorial

Note: Who is this for?
This tutorial is intended to familiarize you with some basic concepts around Django Unicorn. If you have little to no prior experience with Django or other web frameworks, this is a good place to start. However, having basic knowledge of Python and web development concepts will prove helpful.

The goal of this tutorial is to develop a Meal Plan application. With Django Unicorn, you will be able to create "Meals" and add them without refreshing the page. You will also be able to search dynamically for saved Meals.


## Installation

Note: You must have Python installed before starting.

To start with, create a new directory in your terminal where you will build your project. Once you are in this new directory, create a virtual environment and then activate it.

```shell
# Inside your project directory
> python -m venv .venv

# activate environment (MacOs or Linux)
> source .venv/bin/activate
```

Now install Django and Django Unicorn.

```shell
# This installs the Django web framework
> python -m pip install Django

# This installs Django Unicorn
> python -m pip install django-unicorn
```

Now you're ready to create a new Django project. This command will populate your directory with your Django project files and directories.

```shell
django-admin startproject app .
```

(Typing the period `.` in the end will ensure Django is created in your current directory. You can substitute `app` with any other name.)

Once you have created your project, let's build your "Meal Plan" application.

## Create Meal Plan App

You should now have a basic project structure that looks a little like this:

```
my-project/  
┣ .venv/   
┣ mealplan/  
┃ ┣ asgi.py  
┃ ┣ settings.py  
┃ ┣ urls.py  
┃ ┣ wsgi.py  
┃ ┗ __init__.py  
┗ manage.py
```

In order to create your Meal Plan application, make sure that you are in the `my-project` directory and type the following command.

```shell
python manage.py startapp mealplan
```

In this case, `mealplan` is the name of your app. You can choose to name it something different if you prefer.

After running the command, your file structure should look like this.

```
my-project/  
┣ .venv/  
┣ app/  
┃ ┣ asgi.py  
┃ ┣ settings.py  
┃ ┣ urls.py  
┃ ┣ wsgi.py  
┃ ┗ __init__.py  
┣ mealplan/  
┃ ┣ migrations/  
┃ ┣ admin.py  
┃ ┣ apps.py  
┃ ┣ models.py  
┃ ┣ tests.py  
┃ ┣ views.py  
┃ ┗ __init__.py  
┗ manage.py
```

Next, we need to register your `mealplan` app, as well as `Django Unicorn` (which we installed earlier) into the `my-project/app/settings.py` file.

Find the `INSTALLED_APPS` and include them like this:

```python
# app/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_unicorn',
    'mealplan',
]
```

## Creating Models

We will use SQLite as a database for our meal plans. This setting already comes configured with Django, but we must first _create a migration_ which will allow us to use Models to represent the data in the database.

Run the command `python manage.py migrate` and you should see something like this:

```shell
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
```

So let's create a model for our meals.

```python
# mealplan/models.py

from django.db import models

class Meal(models.Model):
    TYPE_OF_MEAL = {
        "B": "Breakfast",
        "L": "Lunch",
        "D": "Dinner",
        "S": "Snack",
    }
    name = models.CharField(max_length=100)
    main_dish = models.CharField(max_length=50)
    side_dish = models.CharField(max_length=50, blank=True)
    desert = models.CharField(max_length=50, blank=True)
    type_of_meal = models.CharField(max_length=1, choices=TYPE_OF_MEAL.items(), blank=True)

    def __str__(self):
        return self.name
```

Now our model is in our codebase, but we also need to add this table to our database. First, we prepare a migration file with instructions on how to do that with the following Django command.

```shell
python manage.py makemigrations mealplan
```

And then, to apply those changes to the database:

```shell
python manage.py migrate mealplan
```

Note: Any time you add or make changes to your models, you need to run these commands to make sure the changes apply to the database.

## URLs

Before we create a page that we can actually _see_, we need to configure the URLs that will lead to our (eventual) content.

Django automatically creates a URL leading to an "Admin" section (you can read more about that in the official Django tutorial).

```python
# app/urls.py

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
```

We want to go ahead and add a pattern that will lead to any URLs defined in your `mealplan` app. Also, Django Unicorn utilizes its own pattern which needs to be added also.

```python
# app/urls.py

from django.contrib import admin
from django.urls import path, include  # Added include

urlpatterns = [
	path('admin/', admin.site.urls),
	path("", include("mealplan.urls")), # Added for your app
	path("unicorn/", include("django_unicorn.urls")), # Added for Django Unicorn
]
```

Django will now redirect everything that goes to your index page to `mealplan.urls`, but you'll note that there is currently not a module (a `.py` file) by that name in your `mealplan` directory. You will need to create it!

```
mealplan/   
┣ migrations/  
┣ admin.py  
┣ apps.py  
┣ models.py  
┣ tests.py  
┣ urls.py  # New!
┣ views.py  
┗ __init__.py
```

In that file, you can define the URLs and what "Views" will be rendered.

```python
# mealplan/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

```

We have not yet created a View called `index` yet, but we're getting there!

## Views

In Django, a _view_ is often where you might include the application logic. It also specifies what will be rendered on the browser, typically HTML contained in a _template_ file.

You should already have a `view.py` file created for your `mealplan` app. Let's open it up and try to render a page.

```python
# mealplan/views.py

from django.shortcuts import render


def index(request) :
    return render(request, "mealplan/meals.html")

```

Here, we're trying to render a template called `meals.html` (it doesn't exist yet). So let's go ahead and build that template, shall we?

## Templates

In Django, there is a naming convention that organizes how _views_ link up to templates, and it relies on a certain directory structure. To create this first template, we need to add two directories and a file like so:

```
mealplan/  
┣ migrations/  
┣ templates/       # New!
┃ ┗ mealplan/      # New!
┃   ┗ meals.html   # New!
┣ admin.py  
┣ apps.py  
┣ models.py  
┣ tests.py  
┣ urls.py  
┣ views.py  
┗ __init__.py
```

Django templates allow you to insert Python into your HTML. Let's build a quick template that will show us a list of all our meals (hint: we don't have any saved yet!)

:::{code} html
:force: true
<!-- mealplan/templates/mealplan/meals.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <title>Meal Plan</title>
    <link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
</head>
<body>
    <main class="container">
        <header>
	        <h1>Meal Plan</h1>
		</header>
        <div>
            <p>No meals have been prepared yet!</p>
            <button>Add a meal</button>
        </div>
        <footer>
            <hr />
            2024 &copy;
        </footer>
    </main>
</body>
</html>

:::

A couple things to note.

We are using a CDN to link to a [SimpleCSS stylesheet](https://https://simplecss.org). This applies specific styling to our webpage. Ordinarily, you would store your CSS files in a Django `static` directory. You can read more about that in the [official Django documentation](https://docs.djangoproject.com/en/5.0/howto/static-files/).

So far, we have a message stating that no meals have been created, as well as a button that is supposed to let us add a meal to our database.

Let's add some logic in the template that will look for a `meals` object (which could be a list of meals saved in our database). If it finds an object (a list of meals), we will _do something_, otherwise, we'll display the message that no meals have been created.

Change the `<div>` section to look like this:

:::{code} html
:force: true
<!-- mealplan/templates/mealplan/meals.html -->

...

<main>
	{% if not meals %}
		<p>No meals have been prepared yet!</p>
	{% else %}
	<ul>
	{% for meal in meals %}
		<li>{{ meal.name }}</li>
	{% endfor %}
	</ul>
	{% endif %}
	<button>Add a meal</button>
</main>

...

:::

The _something_ we are doing is iterating over the `meals` object and creating a new list item (`<li>`) for every meal that we find, and then displaying the name of that meal.

We'll see that in action eventually, but first, we need to provide an ability to create a meal item.

## Creating a Form

In order to allow a user to input the data that we need for our `Meal` table in the database, we have to create an HTML form that allows a user to do that.

Django allows us to create a `Form` object similar to how we created a `Model`, which we could then feed directly to our `template`, which in turn would render the appropriate HTML form in the browser.

However, when using a Django Unicorn "component", you _cannot_ send the `Form` object to the template and render it the same way. But, _we can still use_ a Django `Form` object in order to _validate_ the input data.

This might make more sense when we see it in action. So for now, let's go ahead and create a `Form` object.

Similar to the `url.py` module, we will need to create a `forms.py` file for our `mealplan` app.

```
mealplan/   
┣ migrations/  
┣ admin.py  
┣ apps.py  
┣ forms.py # New! 
┣ models.py  
┣ tests.py  
┣ urls.py
┣ views.py  
┗ __init__.py
```
The `MealForm` model below is linked to the `Meal` object that links to our database. This `ModelForm` now has the _constraints_ we defined in the model (such as the `max_length` of any given field, or whether a field is required or not).

```python
# mealplan/forms.py

from django.forms import ModelForm
from .models import Meal

class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = '__all__'
        labels = {
            "name": "Name",
            "main_dish": "Main dish",
            "side_dish": "Side dish",
            "desert": "Desert",
            "type_of_meal": "Type of meal",
        }

```


## Django Unicorn Setup

Django Unicorn uses the term "[Component](https://www.django-unicorn.com/docs/components/)" to refer to a set (or a block) of interactive functionality. Similar to how your Django _views_ connect to your _templates_, `Unicorn` uses a special [view class](https://www.django-unicorn.com/docs/views/) (`UnicornView`) residing within a special `components` directory linking to a specific _template_ with the _same name_ as the `component` module.

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

You could create those files marked as `#New!` manually, but the command makes it easy for you.

If you build additional components, you would create new files in the `components` directory as well as in the `template/unicorn`directory with the same name (note the distinction between the `.py` and `.html` extensions, as well as the hyphen and underscore).

In order to use components within your regular Django templates, you need to "include" them within your HTML file.

Let's go back to `index.html` and add that.

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

Note: In case you missed it earlier and if you haven't already done so, make sure that `django_unicorn` is listed within your `INSTALLED_APPS` in your `settings.py` file.

## Components

Components are where much of the Django Unicorn heavy lifting occurs. Here, we will define a `UnicornView`, which in turn contains the back end logic which will be passed to the corresponding `template`.

The interaction between the component and the tutorial is unique to this pairing, and it is "included" in your Django templates with a special template tag. The tag contains the name `unicorn`, followed by the name of the template, which in turn corresponds to the component.

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

Note: The term `model` in this particular context _does not_ correlate to a Django `Model`. In other words, `unicorn:model` is what enables reactivity. Django Unicorn holds the fields from the component (`create_model.py`) in a special context. Then, when the element with `unicorn:model` triggers a change (whether on load, click, submit, blur, etc...), then it sends an AJAX request to a specific Unicorn endpoint, and the response is rendered in place. You don't necessarily have to understand all of that, but it's worth noting that `unicorn:model` is _not_ referring to your Django `Model` directly.

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


## Adding Meals 

We have everything set in order to start using our component in very powerful ways. We can now interact with our `CreateMealView` from within any element in the `create-meal.html` template, which enables us to make powerful, reactive functionality _without the need_ of writing any JavaScript.

Next, what we want to do is provide a user with a form so that they can create a new meal to save into the database. But we want to keep that form hidden, unless the user clicks on a button to "Add a Meal."

In our `CreateMealView`, we are going to create a field called `state` which will determine whether a user sees a form or not.

```python
# mealplan/components/create_meal.py

...
class CreateMealView(UnicornView):
    meals: list[Meal] = None

    def mount(self):
	    state: str = "Add"
        self.meals = Meal.objects.all()
```

The value of `state` will be sent over to our template. So now we can create a condition in our template to look for that value.

:::{code} html
:force: true
<!-- mealplan/templates/unicorn/create-meal.html -->

<div>
	{% if state == "Add" %}
	<button unicorn:click="add">Add a Meal</button>
	{% if meals %}
	<button>Clear Meals</button>
	{% endif %}
</div>
	{% else %}
	<button unicorn:click.discard="cancel">Cancel</button>
	<hr />
</div>
:::

The line `{% if state == "Add" %}` compares the `state` field in the component to its value.

Since that is the value that is initially set, we are rendering an "Add a Meal" button. Additionally, if we find any value in the `meals` field (again, in the component), then we will also render a "Clear Meals" button. For now, it doesn't do anything.

But what happens when we _click_ the "Add a Meal" button?

In this case, `unicorn:click` checks our component for a method called `add`, but we have not created it yet, so let's go ahead and do that (along with some logic for the `cancel` action).

```python
# mealplan/components/create_meal.py

...
class CreateMealView(UnicornView):
    state: str = "Add"
    meals: list[Meal] = None

    def mount(self):
        self.meals = Meal.objects.all()

    def add(self):
        self.state = "Cancel"

	def cancel(self):
        self.reset()
        self.state = "Add"
```

Now, when a user clicks on the "Add a Meal" button, the _value_ of the `state` field is going to change to "Cancel".

Our template logic will no longer see "Add" as the value to `state`, so the button that will render next is the "Cancel" button.

Similarly, to change the button back, you follow a similar logic. The only difference we see here is the addition of the `discard` directive. This is to prevent any model updates from being saved (we're getting there).

However, we still need to display the form to users so that they can input a meal. I'm going to provide the entire `create-meal.html` file here and then we can build out the component in the next section.

:::{code} html
:force: true
<!-- mealplan/templates/unicorn/create-meal.html -->

{% load unicorn %}
<div>
    <div unicorn:model.defer = "meals">
        {% if not meals %}
            <p>No meals yet</p>
        {% else %}
        {% for meal in meals %}
            <p>{{ meal.name }}</p>
        {% endfor %}
        {% endif %}
    </div>
    <div>
        {% if state == "Add" %}
        <button unicorn:click="add">Add a Meal</button>
        {% if meals %}
        <button unicorn:click="clear">Clear Meals</button>
        {% endif %}
    </div>
        {% else %}
        <button unicorn:click.discard="cancel">Cancel</button>
        <hr />
    </div>
    <div>
        <label for="name">Name of meal</label>
        <input unicorn:model.defer="name" type="text" id="name" />
        <small style="color:red">&nbsp;{{ unicorn.errors.name.0.message }}</small>
    </div>
    <div>
        <label for="main_dish">Main dish</label>
        <input unicorn:model.defer="main_dish" type="text" id="main_dish" />
        <small style="color:red">&nbsp;{{ unicorn.errors.main_dish.0.message }}</small>
    </div>
    <div>
        <label for="side_dish">Side dish</label>
        <input unicorn:model.defer="side_dish" type="text" id="side_dish" />
    </div>
    <div>
        <label for="desert">Desert</label>
        <input unicorn:model.defer="desert" type="text" id="desert" />
    </div>
    <div>
        <label for="type_of_meal">Type of meal</label>
        <select unicorn:model.defer="type_of_meal" id="id_type_of_meal">
            <option value="" selected="">---------</option>
            <option value="B">Breakfast</option>
            <option value="L">Lunch</option>
            <option value="D">Dinner</option>
            <option value="S">Snack</option>
        </select>
    </div>
    <p>
        <button type=submit unicorn:click="create">Save</button>
    </p>
        {% endif %}
</div>
:::

You'll notice that after the `{% else %}` statement that includes the "Cancel" button, we are also including `<input>` fields that are linked to the `unicorn:model`. Remember, this is _not_ directly the `Meal` model that is connected to our database. Rather, it is what is _binding_ the template to our component. 

Each input is linked to a field in the component that matches the assignment. In other words, the `<input unicorn:model.defer="name" ...>` line is looking for a field called `name` in our component. (Hint: we haven't created that field yet.)

Also, you'll notice the `defer` directive on these inputs. This is is done to store and save model changes until the next action gets triggered (in our case, clicking the "Save" button).

## Backend Logic

We've provided the _ability_ for users to enter meals to the form, but so far, that won't do anything.

As I mentioned in the previous section, the fields referenced in the `<input>` elements haven't been defined. Let's go ahead and add those fields to our `CreateMealView`.

```python
# mealplan/components/create_meal.py

...
class CreateMealView(UnicornView):
    state: str = "Add"
    meals: list[Meal] = Nonename = None
    main_dish = None
    side_dish = None
    desert = None
    type_of_meal = None
    
```

Now take a look at the "submit" button in the `create-meal.html` file. It is looking for a method called `create`, which should handle saving the data from the form to our database.

Django allows us to create a new `Meal` in the database by passing values to the corresponding fields. For the sake of convenience, here is what our model looks like.

```python
# mealplan/models.py

from django.db import models

class Meal(models.Model):
    TYPE_OF_MEAL = {
        "B": "Breakfast",
        "L": "Lunch",
        "D": "Dinner",
        "S": "Snack",
    }
    name = models.CharField(max_length=100)
    main_dish = models.CharField(max_length=50)
    side_dish = models.CharField(max_length=50, blank=True)
    desert = models.CharField(max_length=50, blank=True)
    type_of_meal = models.CharField(max_length=1, choices=TYPE_OF_MEAL.items(), blank=True)

    def __str__(self):
        return self.name
```

In order to create a record in our database, we can use the `Model.objects.create()` method, where the `Model` in question is an instance of `Meal` we have defined above. 

So now, we can introduce a new method in our `CreateMealView` class like this:

```python
# mealplan/components/create_meal.py

...
class CreateMealView(UnicornView):
    state: str = "Add"
    meals: list[Meal] = None

    def mount(self):
        self.meals = Meal.objects.all()

    def add(self):
        self.state = "Cancel"

	def cancel(self):
        self.reset()
        self.state = "Add"

	def create(self):
         _new_meal = Meal.objects.create(
            name=self.name,
            main_dish=self.main_dish,
            side_dish=self.side_dish,
            desert=self.desert,
            type_of_meal=self.type_of_meal
        )
        self.state = "Add"
```

This will create a `_new_meal` when a user clicks on the "Save" button, and it will also turn the `state` field into "Add", which means that our template will hide the form automatically!

## A Few More Things

We've mostly got things working, but there are still some oddities to work out.

For example, we can currently save Meals to our database, but we don't have a way to remove them. Also, when we try to add _new_ Meals by clicking on "Add a Meal," the values of the previous Meal are pre-populated in the `<input>` elements. Additionally, the list of Meals does not refresh after clicking the "Save" button.

First, let's add a method that will remove all the meals we have previously saved. Remember in our template, we have a `unicorn:click.discard="cancel"...` attribute, which means we can create a `cancel` method in our component.

```python
def clear(self):
        _remove_all_meals = Meal.objects.all().delete()
        self.mount()
```

The `self.mount()` method is called after we delete all the meals, which refreshes the component back to the initial state. (Without it, the list of Meals won't disappear until you refresh the component or page.)

Secondly, let's remove the values that appear on the `<input>` elements after saving a Meal. What we can do is add a _special_ method to the `add` method in our component. It will refresh the data so that when the template loads, the items disappear. Django Unicorn provides us with a special method within the `UnicornView` called `reset()`. 

```python
def add(self):
        self.reset()
        self.name = None
        self.main_dish = None
        self.side_dish = None
        self.desert = None
        self.type_of_meal = None
        self.state = "Cancel"
```

And finally, to refresh the list of Meals after saving an object, we just need to refresh the `meals` field in the component. We can do that by making a call to the database after saving.

```python
def create(self):
        _new_meal = Meal.objects.create(
            name=self.name,
            main_dish=self.main_dish,
            side_dish=self.side_dish,
            desert=self.desert,
            type_of_meal=self.type_of_meal
        )

        self.meals = Meal.objects.all()
        self.state = "Add"
```

There is still one last feature we will examine in this tutorial.


## Validation

Remember how we created a `MealForm` in the `forms.py` module?

What can we do with that?

With Django Unicorn, we can use it to validate the data a user might type into the form. Currently, a user could theoretically save an empty form, or include more than the allowed characters on each field.

Let's import our `MealForm` into the `create_meal.py` component, and then add a `form_class` field that references this form. 

```python
# mealplan/components/create_meal.py

from django_unicorn.components import UnicornView

from mealplan.forms import MealForm
from mealplan.models import Meal

class CreateMealView(UnicornView):
    state: str = "Add"
    meals: list[Meal] = None

    form_class = MealForm
    name = None
    main_dish = None
    side_dish = None
    desert = None
    type_of_meal = None
...
```

Now, Django Unicorn knows that we are using the `MealForm` to validate the data we are receiving from the related inputs.

We've included a `{{ unicorn.errors.name.0.message }}` template tag to display any validation errors that occur for the `name` field. 

If you look at the model definition, you'll note that the field cannot be longer than 100 characters. And since the `blank=True` is not part of its definition, it means that it is also a _required_ field.

Although our form will tell us of these validation errors, we also don't want to allow users to be able to _save_ the models if they fail validation.

Django Unicorn provides another special method within a `UnicornView` class to check for validation. We can use that to update our `create` method within the component. 

```python
def create(self):
        if not self.is_valid():
            return

        _new_meal = Meal.objects.create(
            name=self.name,
            main_dish=self.main_dish,
            side_dish=self.side_dish,
            desert=self.desert,
            type_of_meal=self.type_of_meal
        )

        self.meals = Meal.objects.all()
        self.state = "Add"
```

If the data is not valid in the form, the user will see the errors displayed, but they will not be able to `create` the `Meal` object.

And, putting it all together, your `create_meal.py` component should look something like this:

```python
# mealplan/components/create_meal.py

from django_unicorn.components import UnicornView

from mealplan.forms import MealForm
from mealplan.models import Meal

class CreateMealView(UnicornView):
    state: str = "Add"
    meals: list[Meal] = None

    form_class = MealForm
    name = None
    main_dish = None
    side_dish = None
    desert = None
    type_of_meal = None

    def mount(self):
        self.meals = Meal.objects.all()

    def add(self):
        self.reset()
        self.name = None
        self.main_dish = None
        self.side_dish = None
        self.desert = None
        self.type_of_meal = None
        self.state = "Cancel"

    def cancel(self):
        self.reset()
        self.state = "Add"

    def create(self):
        if not self.is_valid():
            return

        _new_meal = Meal.objects.create(
            name=self.name,
            main_dish=self.main_dish,
            side_dish=self.side_dish,
            desert=self.desert,
            type_of_meal=self.type_of_meal
        )

        self.meals = Meal.objects.all()
        self.state = "Add"

    def clear(self):
        _remove_all_meals = Meal.objects.all().delete()
        self.mount()
```

Summary >>

## Summary

Congratulations!

By the end of this tutorial, not only were you able to build a small Django application, but you were also able to incorporate Django Unicorn to allow for some awesome, reactive, and dynamic data manipulation without the need to rely on any external frontend frameworks.

You learned how to create a component/template combo that allows for highly reactive functionality. You were able to change field values dynamically, as well as conduct database operations (creating a record or deleting records) with minimal setup. 

And there's much more to uncover with Django Unicorn. Take a look at the documentation to see what else you can discover!