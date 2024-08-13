# Building a Django App

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