# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0026_auto_20161120_2005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='roles',
            field=models.ManyToManyField(to='opal.Role', blank=True),
        ),
    ]
