# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0032_auto_20171020_1058'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maritalstatus',
            options={'verbose_name_plural': 'Marital statuses'},
        ),
        migrations.AlterModelOptions(
            name='speciality',
            options={'verbose_name_plural': 'Specialities'},
        ),
    ]
