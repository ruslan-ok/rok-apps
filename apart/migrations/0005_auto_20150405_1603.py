# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0004_auto_20150405_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='communal',
            name='period',
            field=models.IntegerField(default=201504),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='month',
            field=models.IntegerField(default=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='period',
            field=models.IntegerField(default=201504),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='year',
            field=models.IntegerField(default=2015),
            preserve_default=True,
        ),
    ]
