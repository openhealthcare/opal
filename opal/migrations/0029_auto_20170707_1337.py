# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0028_auto_20170210_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='macro',
            name='expanded',
            field=models.TextField(help_text=b'This is the text that it will expand to.'),
        ),
    ]
