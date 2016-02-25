# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0006_auto_20151109_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagging',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
