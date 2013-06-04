import os
from django.core.management.base import BaseCommand, CommandError
from options.models import option_models

class Command(BaseCommand):
    help = 'Loads seed data'

    def handle(self, *args, **options):
        seeds_path = os.path.join(os.path.dirname(__file__), '../../seeds')

        for name, model in option_models.items():
            with open(os.path.join(seeds_path, '%s_list' % name)) as f:
                for line in f:
                    option_name = line.strip()
                    model.objects.get_or_create(name=option_name)
