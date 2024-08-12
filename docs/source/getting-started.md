# Getting Started

## Create a Django Project

`Unicorn` requires a working Django project before it can be used. While it is recommended that you have some experience working with Python and Django, below is a list of steps you would need do to use `Unicorn`.

```{dropdown} Install the latest version of Python
`Unicorn` works with Python 3.8 or greater. If you don't have Python installed, you will need to download and install it on your local machine.

You can find the [latest version](https://www.python.org/downloads/) of Python at [python.org](https://www.python.org).

Once you have installed Python, make sure that it has been added to your `PATH`.

`python --version`
```

````{dropdown} Create a virtual environment
Before installing Django, you will need to create a new directory for your project. It is also recommended to create a [virtual environment](https://docs.python.org/3/library/venv.html) where you can install Django, `Unicorn`, and any other dependencies. Once you have created and navigated to the directory, type the following command to create a virtual environment.

`python -m venv .venv`

```{note}
Some package managers automatically create a virtual environment so this step might not be required. But, a virtual environment is suggested if directly using `pip` to install dependencies.
```
````

````{dropdown} Install Django and start a project
You are now ready to install Django and start your project.

```sh
python -m pip install Django
django-admin startproject project-name .
```

If you have never created a Django project before, you may want to get acquainted with it first. There are several resources, including some [official tutorials](https://docs.djangoproject.com/en/stable/intro/), though the [Django Girls Tutorial](https://tutorial.djangogirls.org/en/django_start_project/) is also highly recommended.
````

Once you have a working Django project, you are ready to [install `Unicorn`](installation.md).