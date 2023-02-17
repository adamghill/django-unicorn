import csv

from django.core.management.base import BaseCommand, CommandError

from ...models import Favorite, Flavor


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("example/coffee/management/commands/flavors.csv", "r") as f:
            csv_reader = csv.reader(f)

            for row in csv_reader:
                next(csv_reader)

                name = row[0]
                label = row[1]
                parent_name = row[2]

                parent = Flavor.objects.filter(name=parent_name).first()
                flavor = Flavor(name=name, label=label, parent=parent)
                flavor.save()
                Favorite.objects.create(flavor=flavor)
