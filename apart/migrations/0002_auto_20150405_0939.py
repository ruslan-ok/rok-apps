# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communal',
            name='el_tar',
        ),
        migrations.RemoveField(
            model_name='communal',
            name='gas_tar',
        ),
        migrations.RemoveField(
            model_name='communal',
            name='water_tar',
        ),
        migrations.RemoveField(
            model_name='tarif',
            name='month',
        ),
        migrations.RemoveField(
            model_name='tarif',
            name='year',
        ),
        migrations.AddField(
            model_name='tarif',
            name='period',
            field=models.IntegerField(default=200001),
            preserve_default=True,
        ),
    ]
