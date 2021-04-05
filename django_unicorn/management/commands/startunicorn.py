from pathlib import Path
from webbrowser import open

from django.conf import settings
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


class Command(BaseCommand):
    help = "Creates a new component for `django-unicorn`"

    def add_arguments(self, parser):
        parser.add_argument("component_names", nargs="+", type=str)

    def handle(self, *args, **options):
        if not hasattr(settings, "BASE_DIR"):
            raise CommandError("Can't find BASE_DIR for this project.")

        if "component_names" not in options:
            raise CommandError("Pass in at least one component name.")

        base_path = Path(settings.BASE_DIR)
        first_component = False

        if not (base_path / Path("unicorn")).exists():
            (base_path / Path("unicorn")).mkdir()
            self.stdout.write(
                self.style.SUCCESS(
                    "Created unicorn directory for your first component! ✨\n"
                )
            )

            first_component = True

        for component_name in options["component_names"]:
            snake_case_component_name = convert_to_snake_case(component_name)
            pascal_case_component_name = convert_to_pascal_case(component_name)

            # Create component
            component_base_path = base_path / Path("unicorn") / Path("components")

            if not component_base_path.exists():
                component_base_path.mkdir()

            component_path = component_base_path / Path(
                f"{snake_case_component_name}.py"
            )

            if component_path.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"The component for {snake_case_component_name}.py already exists."
                    )
                )
                return

            component_path.write_text(
                COMPONENT_FILE_CONTENT.format(
                    **{"pascal_case_component_name": pascal_case_component_name}
                )
            )
            self.stdout.write(self.style.SUCCESS(f"Created {component_path}."))

            # Create template
            template_base_path = (
                base_path / Path("unicorn") / Path("templates") / Path("unicorn")
            )

            if not template_base_path.exists():
                if not (base_path / Path("unicorn") / Path("templates")).exists():
                    (base_path / Path("unicorn") / Path("templates")).mkdir()

                template_base_path.mkdir()

            template_path = (
                base_path
                / Path("unicorn")
                / Path("templates")
                / Path("unicorn")
                / Path(f"{component_name}.html")
            )

            if template_path.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"The template for {component_name}.html already exists."
                    )
                )
                return

            template_path.write_text(TEMPLATE_FILE_CONTENT)
            self.stdout.write(self.style.SUCCESS(f"Created {template_path}."))

            if first_component:
                input_value = input(
                    "\nStarring the GitHub repo helps other Django users find Unicorn. Can you star it for me? [y/N] "
                )

                if input_value.strip().lower() in ("y", "yes"):
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

                    open("https://github.com/adamghill/django-unicorn", new=2)
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "Ok, bummer. I hope you will star it for me at https://github.com/adamghill/django-unicorn at some point!"
                        )
                    )

            self.stdout.write(
                self.style.WARNING(
                    "\nMake sure to add '\"unicorn\",' to your INSTALLED_APPS list in your settings file if necessary."
                )
            )
