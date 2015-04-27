# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0009_auto_20150426_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='part',
            name='last_km',
        ),
        migrations.RemoveField(
            model_name='part',
            name='last_mo',
        ),
    ]
