"""
Clear the local lookup lists
"""
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from opal.models import Synonym
from opal.core.lookuplists import LookupList
from opal.utils import write


class Command(BaseCommand):
    """
    Management command to delete all lookuplists and related
    synonyms.
    """
    def delete(self):
        write('Deleting Synonyms')

        for item in Synonym.objects.all():
            item.delete()

        write('Deleting Lookuplists')
        for model in LookupList.__subclasses__():
            for item in model.objects.all():
                item.delete()

    def handle(self, *args, **kw):
        self.delete()
