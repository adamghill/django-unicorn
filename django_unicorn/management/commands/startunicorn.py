from pathlib import Path
from webbrowser import open

from django.core.management.base import BaseCommand, CommandError

from django_unicorn.components.unicorn_view import (
    convert_to_pascal_case,
    convert_to_snake_case,
)


COMPONENT_FILE = """from django_unicorn.components import UnicornView


class {pascal_case_component_name}View(UnicornView):
    pass
"""

TEMPLATE_FILE = """<div>
    <!-- put component code here -->
</div>
"""


class Command(BaseCommand):
    help = "Creates a new component for `django-unicorn`"

    def add_arguments(self, parser):
        parser.add_argument("component_names", nargs="+", type=str)

    def handle(self, *args, **options):
        if not Path("manage.py").exists():
            raise CommandError("Can't find manage.py in current path.")

        first_component = False

        if not Path("unicorn").exists():
            Path("unicorn").mkdir()
            self.stdout.write(
                self.style.SUCCESS(
                    "Create unicorn directory for your first component! ✨"
                )
            )

            first_component = True

        for component_name in options["component_names"]:
            snake_case_component_name = convert_to_snake_case(component_name)
            pascal_case_component_name = convert_to_pascal_case(component_name)

            # Create component
            if not Path("unicorn/components").exists():
                Path("unicorn/components").mkdir()

            component_path = Path(f"unicorn/components/{snake_case_component_name}.py")
            component_path.write_text(
                COMPONENT_FILE.format(
                    **{"pascal_case_component_name": pascal_case_component_name}
                )
            )
            self.stdout.write(self.style.SUCCESS(f"Created {component_path}."))

            # Create template
            if not Path("unicorn/templates/unicorn").exists():
                if not Path("unicorn/templates").exists():
                    Path("unicorn/templates").mkdir()

                Path("unicorn/templates/unicorn").mkdir()

            template_path = Path(f"unicorn/templates/unicorn/{component_name}.html")
            template_path.write_text(TEMPLATE_FILE)
            self.stdout.write(self.style.SUCCESS(f"Created {template_path}."))

            if first_component:
                input_value = input(
                    "\nStarring the GitHub repo helps other Django users find Unicorn. Can you star it for me? [y/N] "
                )

                if input_value.strip().lower() in ("y", "yes"):
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
                    self.stdout.write(
                        self.style.SUCCESS(
                            "Thank you for helping spread the word about Unicorn!"
                        )
                    )
                    open("https://github.com/adamghill/django-unicorn", new=2)

            self.stdout.write(
                self.style.WARNING(
                    "\nMake sure to add '\"unicorn\",' to your INSTALLED_APPS list in your settings file if necessary."
                )
            )
