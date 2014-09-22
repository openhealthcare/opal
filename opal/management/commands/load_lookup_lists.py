"""
Load a series of lookup lists into our instance.
"""
from optparse import make_option

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
import ffs

from opal.models import Synonym
from opal.utils.models import LookupList

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

    def _from_file(self, filename):
        datafile = ffs.Path(filename)
        return datafile.json_load()

    def _install_item(self, model, item):
        content_type = ContentType.objects.get_for_model(model)
        instance, _ = model.objects.get_or_create(name=item['name'])
        for synonym in item['synonyms']:
            syn, _ = Synonym.objects.get_or_create(
                content_type=content_type,
                object_id=instance.id,
                name=synonym
            )
        return
    
    def handle(self, *args, **options):
        if options['filename']:
            data = self._from_file(options['filename'])
        else:
            raise ValueError('no lookuplist_provided!')
            
        for model in LookupList.__subclasses__():
            name = model.__name__.lower()
            if name in data:
                for item in data[name]:
                    self._install_item(model, item)
                
        print data
        return
