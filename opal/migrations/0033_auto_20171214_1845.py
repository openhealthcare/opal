# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0032_auto_20171020_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='created_by',
            field=models.ForeignKey(related_name='created_opal_episode_subrecords', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_opal_episode_subrecords', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='inpatientadmission',
            name='created_by',
            field=models.ForeignKey(related_name='created_opal_inpatientadmission_subrecords', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='inpatientadmission',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_opal_inpatientadmission_subrecords', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='tagging',
            name='created_by',
            field=models.ForeignKey(related_name='created_opal_tagging_subrecords', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='tagging',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_opal_tagging_subrecords', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
