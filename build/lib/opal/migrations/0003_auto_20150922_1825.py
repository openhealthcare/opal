# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0002_auto_20150822_0820'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='created',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='episode',
            name='created_by',
            field=models.ForeignKey(related_name='created_opal_episode_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='episode',
            name='updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='episode',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_opal_episode_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tagging',
            name='created',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tagging',
            name='created_by',
            field=models.ForeignKey(related_name='created_opal_tagging_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tagging',
            name='updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tagging',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_opal_tagging_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
        ),
    ]
