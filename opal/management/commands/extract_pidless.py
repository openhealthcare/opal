"""
Dumps data w/out PID.
"""
import sys

import json
import StringIO

from django.core.management.commands import dumpdata

class Command(dumpdata.Command):
    def handle(self, *app_labels, **options):
        # Parent class writes to stdout so let's fake that.
        self._stdout = self.stdout
        self.stdout = StringIO.StringIO()

        options['use_natural_foreign_keys'] = True

        model_list = dumpdata.Command.handle(self, *app_labels, **options)

        self.stdout.seek(0)
        models = json.loads(self.stdout.read())

        for i, m in enumerate(models):
            if m['model'].endswith('demographics'):
                models[i]['fields']['hospital_number'] = '555-%s' % i
                models[i]['fields']['date_of_birth'] = '1876-01-01'
                models[i]['fields']['name'] = 'Some Doe%s' % i
            if m['model'].endswith('location'):
                models[i]['fields']['hospital'] = 'INPATIENT HOSPITAL'
                models[i]['fields']['ward'] = 'Ward 1'
                models[i]['fields']['bed'] = str(i)
            if m['model'] == 'opal.episode':
                models[i]['fields']['date_of_admission'] = '1899-01-02'
                models[i]['fields']['discharge_date'] = '1899-02-01'
            pass
        self._stdout.write(json.dumps(models, indent=2))
        return model_list
