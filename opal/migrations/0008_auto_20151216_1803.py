# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0007_tagging_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='category',
            field=models.CharField(default=b'Inpatient', max_length=200),
        ),
    ]
