import os
import webbrowser
from pathlib import Path

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
        parser.add_argument(
            "component_names", nargs="+", type=str, help="Names of components"
        )

    def handle(self, *args, **options):
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
        except LookupError:
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
                )

        is_first_component = False

        if not app_directory.exists():
            app_directory.mkdir()

        # Create component
        component_base_path = app_directory / "components"

        if not component_base_path.exists():
            component_base_path.mkdir()

            self.stdout.write(
                self.style.SUCCESS(f"Created your first component in '{app_name}'! ✨\n")
            )

            is_first_component = True

        (component_base_path / "__init__.py").touch(exist_ok=True)

        nested_paths = []

        for component_name in options["component_names"]:
            if "." in component_name:
                (*nested_paths, component_name) = component_name.split(".")

                for nested_path in nested_paths:
                    component_base_path /= nested_path

                    if not component_base_path.exists():
                        component_base_path.mkdir()

                    (component_base_path / "__init__.py").touch(exist_ok=True)

            snake_case_component_name = convert_to_snake_case(component_name)
            pascal_case_component_name = convert_to_pascal_case(component_name)

            component_path = component_base_path / f"{snake_case_component_name}.py"

            if component_path.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"Skipping creating {snake_case_component_name}.py because it already exists."
                    )
                )
            else:
                component_path.write_text(
                    COMPONENT_FILE_CONTENT.format(
                        **{"pascal_case_component_name": pascal_case_component_name}
                    )
                )
                self.stdout.write(self.style.SUCCESS(f"Created {component_path}."))

            # Create template
            template_base_path = app_directory / "templates" / "unicorn"

            if not template_base_path.exists():
                if not (app_directory / "templates").exists():
                    (app_directory / "templates").mkdir()

                template_base_path.mkdir()

            for nested_path in nested_paths:
                template_base_path /= nested_path

                if not template_base_path.exists():
                    template_base_path.mkdir()

            template_path = template_base_path / f"{component_name}.html"

            if template_path.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"Skipping creating {component_name}.html because it already exists."
                    )
                )
            else:
                template_path.write_text(TEMPLATE_FILE_CONTENT)
                self.stdout.write(self.style.SUCCESS(f"Created {template_path}."))

            if is_first_component:
                will_star_repo = input(
                    "\nStarring the GitHub repo helps other Django users find Unicorn. Can you star it for me? [y/N] "
                )

                if will_star_repo.strip().lower() in ("y", "yes"):
                    self.stdout.write(
                        self.style.SUCCESS(
                            "Thank you for helping spread the word about Unicorn!"
                        )
                    )

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

                    webbrowser.open(
                        "https://github.com/adamghill/django-unicorn", new=2
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "That's a bummer, but I understand. I hope you will star it for me later!"
                        )
                    )

            if is_new_app:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nMake sure to add `"{app_name}",` to your INSTALLED_APPS list in your settings file if necessary.'
                    )
                )
