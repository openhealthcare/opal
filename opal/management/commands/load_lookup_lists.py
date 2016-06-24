"""
Load a series of lookup lists into our instance.
"""
import logging
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
import ffs

from opal.models import Synonym
from opal.core.lookuplists import LookupList

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "-f",
            "--file",
            dest = "filename",
            help = "specify import file",
            metavar = "FILE"
        ),
    )
    def __init__(self, *args, **kwargs):
        self.items_created = 0
        self.synonyms_created = 0
        super(Command, self).__init__(*args, **kwargs)

    def _from_file(self, filename):
        datafile = ffs.Path(filename)
        return datafile.json_load()

    def _install_item(self, model, item):
        content_type = ContentType.objects.get_for_model(model)
        instance, created = model.objects.get_or_create(name=item['name'])
        if created:
            self.items_created += 1
        for synonym in item['synonyms']:
            syn, created = Synonym.objects.get_or_create(
                content_type=content_type,
                object_id=instance.id,
                name=synonym
            )
            if created:
                self.synonyms_created += 1
        return

    def handle(self, *args, **options):
        if options.get('filename', None):
            data = self._from_file(options['filename'])
        else:
            raise ValueError('no lookuplist_provided!')

        num = 0
        for model in LookupList.__subclasses__():
            name = model.__name__.lower()
            if name in data:
                logging.info('Loading {0}'.format(name))
                num += 1

                for item in data[name]:
                    self._install_item(model, item)

        msg = "\nLoaded {0} lookup lists\n".format(num)
        msg += "\n\nNew items report:\n\n\n"
        msg += "{0} new items".format(self.items_created)
        msg += " {0} new synonyms".format(self.synonyms_created)
        msg += "\n\nEnd new items report."
        self.stdout.write(msg)
        return
