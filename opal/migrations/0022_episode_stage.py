# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0021_patientconsultationreasonforinteraction'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='stage',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
