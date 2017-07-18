# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from opal.models import Episode

from django.db import migrations, models


def add(apps, schema_editor):
    episodes = Episode.objects.all()

    for e in episodes:
        e._start = e.start
        e._end = e.end
        e.save()


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0030_auto_20170718_1340'),
    ]

    operations = [
        migrations.RunPython(add)
    ]
