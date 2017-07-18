# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0031_auto_20170718_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episode',
            name='_end',
        ),
        migrations.RemoveField(
            model_name='episode',
            name='_start',
        ),
        migrations.AddField(
            model_name='episode',
            name='end',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='episode',
            name='start',
            field=models.DateField(null=True, blank=True),
        ),
    ]
