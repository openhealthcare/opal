# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0014_auto_20160330_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inpatientadmission',
            name='datetime_of_admission',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='inpatientadmission',
            name='datetime_of_discharge',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
