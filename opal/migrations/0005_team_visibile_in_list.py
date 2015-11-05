# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0004_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='visibile_in_list',
            field=models.BooleanField(default=True),
        ),
    ]
