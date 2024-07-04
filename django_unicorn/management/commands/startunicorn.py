import os
import webbrowser
from pathlib import Path
from typing import Dict, Tuple

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from django_unicorn.components.unicorn_view import (
    convert_to_pascal_case,
    convert_to_snake_case,
)

COMPONENT_FILE_CONTENT = """from django_unicorn.components import UnicornView


class {pascal_case_component_name}View(UnicornView):
    pass
"""

TEMPLATE_FILE_CONTENT = """<div>
    <!-- put component code here -->
</div>
"""


def get_app_path(app_name: str) -> Path:
    """
    Gets the directory path for an installed application.
    """

    return Path(apps.get_app_config(app_name).path)


class Command(BaseCommand):
    help = "Creates a new component for `django-unicorn`"

    def add_arguments(self, parser):
        parser.add_argument("app_name", type=str)
        parser.add_argument("component_names", nargs="+", type=str, help="Names of components")

    def check_initials_directories(self, app_directory: Path) -> Tuple[Dict[str, Path], bool]:
        """
        Checks for directories existance and creates them if necessary.
        Returns a tuple containing a dictonary `components` and `templates`
        keys, and a boolean indicating if directories were created.
        """

        paths = {
            "components": app_directory / "components",
            "templates": app_directory / "templates" / "unicorn",
        }

        is_first = False

        if not paths["components"].exists():
            paths["components"].mkdir()
            self.stdout.write(self.style.SUCCESS(f"Created your first component in '{app_directory.name}'! ✨\n"))
            is_first = True

        (paths["components"] / "__init__.py").touch(exist_ok=True)

        if not paths["templates"].exists():
            paths["templates"].mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f"Created your first template in '{app_directory.name}'! ✨\n"))
            is_first = True

        return paths, is_first

    def obtain_nested_path(self, component_name: str) -> Tuple[str, str]:
        """
        Receives the complete component name and returns a tuple
        with the nested path and component name itself.
        """

        nested_paths = []

        if "." in component_name:
            (*nested_paths, component_name) = component_name.split(".")

        return "/".join(nested_paths), component_name

    def create_nested_directories(self, paths: Dict[str, Path], nested_path: str) -> None:
        """
        Creates the nested directories for the components and templates.
        """

        nested_paths = nested_path.split("/")

        component_path = paths["components"]
        template_path = paths["templates"]

        for _nested_path in nested_paths:
            component_path /= _nested_path
            template_path /= _nested_path

            if not component_path.exists():
                component_path.mkdir()

            if not template_path.exists():
                template_path.mkdir()

            (component_path / "__init__.py").touch(exist_ok=True)

    def create_component_and_template(self, paths: Dict[str, Path], nested_path: str, component_name: str) -> None:
        """
        Creates the component and template files.
        """

        snake_case_component_name = convert_to_snake_case(component_name)
        pascal_case_component_name = convert_to_pascal_case(component_name)

        component_path = paths["components"] / nested_path / f"{snake_case_component_name}.py"

        if component_path.exists():
            self.stdout.write(
                self.style.ERROR(f"Skipping creating {snake_case_component_name}.py because it already exists.")
            )
        else:
            component_path.write_text(
                COMPONENT_FILE_CONTENT.format(**{"pascal_case_component_name": pascal_case_component_name})
            )
            self.stdout.write(self.style.SUCCESS(f"Created {component_path}."))

        template_path = paths["templates"] / nested_path / f"{component_name}.html"

        if template_path.exists():
            self.stdout.write(self.style.ERROR(f"Skipping creating {component_name}.html because it already exists."))
        else:
            template_path.write_text(TEMPLATE_FILE_CONTENT)
            self.stdout.write(self.style.SUCCESS(f"Created {template_path}."))

    def ask_for_star_repo(self) -> None:
        will_star_repo = input(
            "\nStarring the GitHub repo helps other Django users find Unicorn. Can you star it for me? [y/N] "
        )

        if will_star_repo.strip().lower() in ("y", "yes"):
            self.stdout.write(self.style.SUCCESS("Thank you for helping spread the word about Unicorn!"))

            self.stdout.write(
                """
                         ,/
                        //
                      ,//
          __    /|   |//
      `__/\\_ --(/|___/-/
   \\|\\_-\\___ __-_`- /-/ \\.
  |\\_-___,-\\_____--/_)' ) \\
   \\ -_ /     __ \\( `( __`\\|
   `\\__|      |\\)      (/|
',--//-|      \\    | '   /
  /,---|       \\        /
 `_/ _,'        |      |
 __/'/          |      |
 ___/           \\ (  ) /
                 \\____/\\
                        \\
"""
            )

            webbrowser.open("https://github.com/adamghill/django-unicorn", new=2)
        else:
            self.stdout.write(
                self.style.ERROR("That's a bummer, but I understand. I hope you will star it for me later!")
            )

    def handle(self, **options):
        # Default from `django-cookiecutter`
        base_path = getattr(settings, "APPS_DIR", None)

        if not base_path:
            # Default from new Django project
            base_path = getattr(settings, "BASE_DIR", None)

        if not base_path:
            # Fallback to the current directory
            base_path = os.getcwd()

        base_path = Path(base_path)

        if "app_name" not in options:
            raise CommandError("An application name is required.")

        if "component_names" not in options:
            raise CommandError("At least one component name is required.")

        app_name = options["app_name"]
        is_new_app = False

        try:
            app_directory = get_app_path(app_name)
        except LookupError as e:
            should_create_app = input(
                f"\n'{app_name}' cannot be found. Should it be created automatically with `startapp {app_name}`? [y/N] "
            )

            if should_create_app.strip().lower() in ("y", "yes"):
                call_command(
                    "startapp",
                    app_name,
                    verbosity=0,
                )
                app_directory = base_path / app_name

                is_new_app = True
            else:
                raise CommandError(
                    f"An app named '{app_name}' does not exist yet. You might need to create it first."
                ) from e

        if not app_directory.exists():
            app_directory.mkdir()

        paths, is_first = self.check_initials_directories(app_directory)

        for component_name in options["component_names"]:
            (nested_path, name) = self.obtain_nested_path(component_name)

            self.create_nested_directories(paths, nested_path)

            self.create_component_and_template(paths, nested_path, name)

            if is_first:
                self.ask_for_star_repo()
                is_first = False

            if is_new_app:
                msg = f'\nMake sure to add `"{app_name}",` to your INSTALLED_APPS list in your settings file if necessary.'  # noqa: E501
                self.stdout.write(self.style.WARNING(msg))
