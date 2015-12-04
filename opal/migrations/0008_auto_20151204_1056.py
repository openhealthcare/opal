# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0007_auto_20151117_1249'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tagging',
            unique_together=set([]),
        ),
    ]
