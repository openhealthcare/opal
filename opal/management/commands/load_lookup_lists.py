"""
Load a series of lookup lists into our instance.
"""
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
        if options['filename']:
            data = self._from_file(options['filename'])
        else:
            raise ValueError('no lookuplist_provided!')

        num = 0
        for model in LookupList.__subclasses__():
            name = model.__name__.lower()
            # print name, (name in data)
            # if name == 'drug':
            #     import pdb;pdb.set_trace()
            #     print data[name]
            if name in data:
                print 'Loading', name
                num += 1

                for item in data[name]:
                    self._install_item(model, item)
        print "\nLoaded", num, "lookup lists\n"
        print "\n\nNew items report:\n\n\n"
        print "{0} new items".format(self.items_created)
        print "{0} new synonyms".format(self.synonyms_created)
        print "\n\nEnd new items report."
        return
