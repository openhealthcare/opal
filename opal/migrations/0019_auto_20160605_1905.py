# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import opal.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0018_auto_20160603_0934'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferralRoute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('internal', models.NullBooleanField()),
                ('referral_route', models.CharField(max_length=255, blank=True)),
                ('referral_name', models.CharField(max_length=255, blank=True)),
                ('date_of_referral', models.DateField(null=True, blank=True)),
                ('referral_team', models.CharField(max_length=255, blank=True)),
                ('referral_reason', models.CharField(max_length=255, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_opal_referralroute_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, models.Model),
        ),
        migrations.AlterField(
            model_name='episode',
            name='category_name',
            field=models.CharField(default=b'TB', max_length=200),
        ),
        migrations.AddField(
            model_name='referralroute',
            name='episode',
            field=models.ForeignKey(to='opal.Episode'),
        ),
        migrations.AddField(
            model_name='referralroute',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_opal_referralroute_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
