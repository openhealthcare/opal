# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0025_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='team',
            name='useful_numbers',
        ),
        migrations.RemoveField(
            model_name='tagging',
            name='team',
        ),
        migrations.DeleteModel(
            name='Team',
        ),
    ]
