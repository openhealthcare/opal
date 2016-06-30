# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0022_episode_stage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReferralReason',
            new_name='ReferralType',
        ),
    ]
