from django.core.management.base import BaseCommand
from opal.core import scaffold as core_scaffold


class Command(BaseCommand):
    help = "creates migrations, migrates, and create record and form templates \
for subrecords in an app"

    def add_arguments(self, parser):
        parser.add_argument('app', help="Specify an app")
        parser.add_argument(
            '--dry-run',
            action='store_true'
        )
        parser.add_argument(
            '--no-migrations',
            action='store_true'
        )

    def handle(self, *args, **options):
        core_scaffold.scaffold_subrecords(
            options['app'],
            migrations=not options['no_migrations'],
            dry_run=options['dry_run']
        )
