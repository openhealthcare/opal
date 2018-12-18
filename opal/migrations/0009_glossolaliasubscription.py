# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0008_auto_20151216_1803'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlossolaliaSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subscription_type', models.CharField(default=b'all_information', max_length=2, choices=[(b'all_information', b'All Information'), (b'core_demographics', b'Core Demographics')])),
                ('gloss_id', models.IntegerField()),
                ('patient', models.ForeignKey(to='opal.Patient', on_delete=models.CASCADE)),
            ],
        ),
    ]
