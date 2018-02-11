from django.core.management.base import BaseCommand, CommandError
from opal.core import scaffold as core_scaffold
from django.apps import apps


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', help="Specify an app")
        parser.add_argument(
            '--dry_run',
            action='store_true'
        )
        parser.add_argument(
            '--no_migrations',
            action='store_true'
        )

    def handle(self, *args, **options):
        if options['app'] not in apps.all_models:
            raise CommandError(
                'App "{}" does not exist'.format(options['app'])
            )
        core_scaffold.buildout(
            options['app'],
            migrations=not options['no_migrations'],
            dry_run=options['dry_run']
        )
