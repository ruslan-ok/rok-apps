# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0002_auto_20150406_2257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='date',
        ),
    ]
