# Features

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