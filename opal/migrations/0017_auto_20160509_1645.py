# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0016_tagging_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='inpatientadmission',
            name='external_system',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='inpatientadmission',
            name='external_identifier',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
