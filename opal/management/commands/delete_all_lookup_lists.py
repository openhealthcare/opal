"""
Clear the local lookup lists
"""
from django.core.management.base import BaseCommand

from opal.models import Synonym
from opal.utils.models import LookupList

class Command(BaseCommand):
    def handle(self, *args, **kw):
        for model in LookupList.__subclasses__():
            for item in model.objects.all():
                item.delete()
        for item in Synonym.objects.all():
            item.delete()
