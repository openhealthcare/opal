# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def import_from_teams(apps, schema_editor):
    Tagging = apps.get_model('opal', 'Tagging')
    for tag in Tagging.objects.all():
        if tag.team:
            tag.value = tag.team.name
            tag.save()
    return

def export_to_teams(apps, schema_editor):
    msg = "Can't revert Tagging-Teams coupling migration - don't know how to convert {0}"
    Tagging = apps.get_model('opal', 'Tagging')
    Team = apps.get_model('opal', 'Team')
    for tag in Tagging.objects.filter(team__isnull=True):
        if Team.objects.filter(name=tag.value).count() < 1:
            raise ValueError(msg.format(tag.value))

    return

class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0015_auto_20160330_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagging',
            name='value',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.RunPython(import_from_teams, export_to_teams)
    ]
