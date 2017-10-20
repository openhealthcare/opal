# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0031_auto_20170719_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episode',
            name='date_of_admission',
        ),
        migrations.RemoveField(
            model_name='episode',
            name='date_of_episode',
        ),
        migrations.RemoveField(
            model_name='episode',
            name='discharge_date',
        ),
    ]
