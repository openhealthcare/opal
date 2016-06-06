# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0019_auto_20160605_1905'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referralroute',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='referralroute',
            name='episode',
        ),
        migrations.RemoveField(
            model_name='referralroute',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='ReferralRoute',
        ),
    ]
