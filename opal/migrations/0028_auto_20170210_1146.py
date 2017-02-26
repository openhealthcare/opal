# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0027_auto_20170114_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='macro',
            name='title',
            field=models.CharField(help_text=b'The text that will display in the dropdown. No spaces!', max_length=200),
        ),
    ]
