"""
Load a series of lookup lists into our instance.
"""
import collections
import json
import os

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from opal.models import Synonym
from opal.core import application, lookuplists


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--many-files',
            help="Write the lookuplists to many different files in "
            "./data/lookuplists",
            action="store_true",
            dest="many_files"
        )

    def _to_json(self, data):
        self.stdout.write(json.dumps(data, indent=2))
        return

    def write_to_file(self, data, filename):
        self.stdout.write("Writing lookuplist data to {0}\n".format(filename))
        with open(filename, 'w') as fh:
            fh.write(json.dumps(data, indent=2))

    def write_to_many_files(self, data):
        app_dir = application.get_app().directory()
        for listname in data:
            filepath = os.path.abspath(
                os.path.join(
                    app_dir, 'data', 'lookuplists', '{0}.json'.format(listname)
                )
            )
            contents = {listname: data[listname]}
            self.write_to_file(contents, filepath)

    def handle(self, *args, **options):
        data = collections.defaultdict(dict)

        for model in lookuplists.lookuplists():
            content_type = ContentType.objects.get_for_model(model)
            items = []
            for item in model.objects.all():
                synonyms = [s.name for s in
                            Synonym.objects.filter(content_type=content_type,
                                                   object_id=item.id)]
                entry = {'name': item.name, 'synonyms': synonyms}
                if item.code and item.system:
                    entry['coding'] = {
                        'code'  : item.code,
                        'system': item.system
                    }
                items.append(entry)
            data[model.__name__.lower()] = items

        if options.get('many_files', False):
            self.write_to_many_files(data)
        else:
            self._to_json(data)
        return
