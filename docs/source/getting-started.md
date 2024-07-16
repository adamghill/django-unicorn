# Getting Started

## Create a Django Project

Django `Unicorn` does not come bundled with `Django`, which means you will first need to have a working
Django project in order to take advantage of `Unicorn`. While it is recommended that you have some experience
working with Python and Django, below is a list of steps you would need to take in order to begin working with
Django `Unicorn`.

```{dropdown} Install the latest version of Python
Django `Unicorn` will work with Python 3.8 or greater. But if you don't have Python installed, you will need to
download and install it on your local machine.

You can find the [latest version](https://www.python.org/downloads/) of Python at [Python.org](https://www.python.org).

Once you have installed Python, make sure that it has been added to your PATH. You can check if it is in your path by opening
up a Terminal and checking for your version of Python.

`python --version`

```

```{dropdown} Create a virtual environment
Before installing Django, you will want to create a new directory for your project. It is also recommended that you create a "virtual environment" where you can install Django, Django Unicorn, and any other dependencies. Once you have created and navigated to the directory, type the following command to create a virtual environment.

`python -m venv .venv`
```

```{dropdown} Install Django and start a project
You are now ready to install Django and start your project. 

`python -m pip install django`


If you have never created a Django project before, you may want to get acquainted with the library first. There are several resources you could use, though I highly recommend the [Django Girls Tutorial](https://tutorial.djangogirls.org/en/django_start_project/).

At the very least, this will include the `django-admin` command, which will generate a project structure for you.

`django-admin startproject project-name .`
```

Once you have a working Django project, you are ready to [install Django Unicorn](installation.md).