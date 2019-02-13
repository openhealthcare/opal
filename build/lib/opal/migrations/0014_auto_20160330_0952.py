# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0013_inpatientadmission'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inpatientadmission',
            old_name='bed',
            new_name='bed_code',
        ),
        migrations.RenameField(
            model_name='inpatientadmission',
            old_name='admitted',
            new_name='datetime_of_admission',
        ),
        migrations.RenameField(
            model_name='inpatientadmission',
            old_name='discharged',
            new_name='datetime_of_discharge',
        ),
        migrations.RenameField(
            model_name='inpatientadmission',
            old_name='ward',
            new_name='ward_code',
        ),
        migrations.AddField(
            model_name='inpatientadmission',
            name='room_code',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
