import os
import sys
from django.core.management.base import BaseCommand, CommandError
from options.models import option_models

_, COLUMNS = map(int, os.popen('stty size', 'r').read().split())

def feeder():
    """
    Generator to give visual comforting visual feedback
    that 'something' is 'happening'
    """
    count = 0
    while True:
        sys.stdout.write('.')
        count += 1
        if count % COLUMNS == 0:
            sys.stdout.write('\n')
            count = 0
        sys.stdout.flush()
        yield

class Command(BaseCommand):
    help = 'Loads seed data'

    def handle(self, *args, **options):
        feedback = feeder()
        seeds_path = os.path.join(os.path.dirname(__file__), '../../seeds')

        for name, model in option_models.items():
            with open(os.path.join(seeds_path, '%s_list' % name)) as f:
                for line in f:
                    option_name = line.strip()
                    model.objects.get_or_create(name=option_name)
                    feedback.next()
        sys.stdout.write('\n')
        sys.stdout.flush()
