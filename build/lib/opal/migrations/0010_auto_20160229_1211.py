# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opal', '0009_glossolaliasubscription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='glossolaliasubscription',
            name='patient',
        ),
        migrations.DeleteModel(
            name='GlossolaliaSubscription',
        ),
    ]
