# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0017_auto_20160509_1645'),
    ]

    operations = [
        migrations.RenameField(
            model_name='episode',
            old_name='category',
            new_name='category_name',
        ),
    ]
