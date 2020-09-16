from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ...components import convert_to_camel_case, convert_to_snake_case


COMPONENT_FILE = """from django_unicorn.components import UnicornView


class {camel_case_component_name}View(UnicornView):
    pass
"""

TEMPLATE_FILE = """<div>
    <!-- put code here -->
    <div style="display:flex; ">
  <img style="height:25px" src="https://static.djangoproject.com/img/logos/django-logo-positive.png">
    <div>🦄</div>
  </span>

</div>
"""


class Command(BaseCommand):
    help = "Creates a new component for `django-unicorn`"

    def add_arguments(self, parser):
        parser.add_argument("component_names", nargs="+", type=str)

    def handle(self, *args, **options):
        if not Path("manage.py").exists():
            raise CommandError("Can't find manage.py in current path.")

        if not Path("unicorn").exists():
            Path("unicorn").mkdir()
            self.stdout.write(self.style.SUCCESS("Create unicorn directory ✨"))

        for component_name in options["component_names"]:
            snake_case_component_name = convert_to_snake_case(component_name)
            camel_case_component_name = convert_to_camel_case(component_name)

            # Create component
            if not Path("unicorn/components").exists():
                Path("unicorn/components").mkdir()

            component_path = Path(f"unicorn/components/{snake_case_component_name}.py")
            component_path.write_text(
                COMPONENT_FILE.format(
                    **{"camel_case_component_name": camel_case_component_name}
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
