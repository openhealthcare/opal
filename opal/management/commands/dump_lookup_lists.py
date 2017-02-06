"""
Load a series of lookup lists into our instance.
"""
import collections
import json

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from opal.models import Synonym
from opal.core.lookuplists import LookupList


class Command(BaseCommand):

    def _to_json(self, data):
        self.stdout.write(json.dumps(data, indent=2))
        return

    def handle(self, *args, **options):
        data = collections.defaultdict(dict)

        for model in LookupList.__subclasses__():
            content_type = ContentType.objects.get_for_model(model)
            items = []
            for item in model.objects.all():
                synonyms = [s.name for s in
                            Synonym.objects.filter(content_type=content_type,
                                                   object_id=item.id)]
                items.append({'name': item.name, 'synonyms': synonyms})
            data[model.__name__.lower()] = items

        self._to_json(data)
        return
