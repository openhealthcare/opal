import os
from django.core.management.base import BaseCommand, CommandError
from options.models import Destination

class Command(BaseCommand):
    help = 'Loads seed data'

    def handle(self, *args, **options):
        seeds_path = os.path.join(os.path.dirname(__file__), '../../seeds')

        with open(os.path.join(seeds_path, 'destinations')) as f:
            for line in f:
                name = line.strip()
                Destination.objects.create(name=name)
