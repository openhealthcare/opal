# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0005_team_visibile_in_list'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='visibile_in_list',
            new_name='visible_in_list',
        ),
    ]
