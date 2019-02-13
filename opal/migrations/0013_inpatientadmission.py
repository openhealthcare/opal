# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import opal.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0012_maritalstatus_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='InpatientAdmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('admitted', models.DateTimeField()),
                ('discharged', models.DateTimeField()),
                ('hospital', models.CharField(max_length=255, blank=True)),
                ('ward', models.CharField(max_length=255, blank=True)),
                ('bed', models.CharField(max_length=255, blank=True)),
                ('admission_diagnosis', models.CharField(max_length=255, blank=True)),
                ('external_identifier', models.CharField(max_length=255, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_opal_inpatientadmission_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
                ('patient', models.ForeignKey(to='opal.Patient', on_delete=models.CASCADE)),
                ('updated_by', models.ForeignKey(related_name='updated_opal_inpatientadmission_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, models.Model),
        ),
    ]
