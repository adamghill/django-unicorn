# Finished App

If you have followed along, your app should be ready to run!

However, in case you missed something, you can reference the [final code for this tutorial](https://github.com/tataraba/django-unicorn-tutorial-app) on GitHub.

```{note}
The example on GitHub also registered the `Meal` in the `mealplan/admin.py` module, making it available in the Django Admin section. This allows you to create/delete Meals by creating and logging in to your site's admin section. You can read more about the [admin section on the Django documentation](https://docs.djangoproject.com/en/5.0/intro/tutorial02/#introducing-the-django-admin). 
```

By this point, you should be able to run your app with the Django command.

```shell
python manage.py runserver
```

You can now go to [http://127.0.0.1:8000](http://127.0.0.1:8000) on your browser to see your app in action.

When you first open the app, it should look something like this:

```{image} img/mealplan-home.png
:alt: Browser displaying Meal Plan app with Add a Meal button
:class: bg-primary
:width: 400px
:align: center
```

When you click to "Add a Meal," you will then see the form populate below.

```{image} img/mealplan-form.png
:alt: Browser displaying Meal Plan app with input elements for Meal
:class: bg-primary
:width: 400px
:align: center
```


And finally, after adding a few meals, you should see a list of them populate, as well as a button to _clear_ the list and start over.

```{image} img/mealplan-saved.png
:alt: Browser displaying Meal Plan app with two listed items
:class: bg-primary
:width: 400px
:align: center
```

Give it a try!
