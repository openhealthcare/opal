# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import opal.models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0018_auto_20160603_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='category_name',
            field=models.CharField(default=opal.models.get_default_episode_type, max_length=200),
        ),
    ]
