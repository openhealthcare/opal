# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_forwards(apps, schema_editor):
    Episode = apps.get_model("opal", "Episode")
    for e in Episode.objects.all():
        if e.date_of_episode:
            e.start = e.date_of_episode
            e.end = e.date_of_episode
        else:
            e.start = e.date_of_admission
            e.end = e.discharge_date

        e.save()


def migrate_backwards(app, schema_editor):
    Episode = app.get_model("opal", "Episode")
    for e in Episode.objects.all():
        e.date_of_admission = e.start
        e.discharge_date = e.end
        e.save()


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0030_auto_20170719_1016'),
    ]

    operations = [
        migrations.RunPython(
            migrate_forwards, reverse_code=migrate_backwards
        ),
    ]
