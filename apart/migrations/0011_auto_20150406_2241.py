# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0010_auto_20150406_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communal',
            name='dCounter',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='dPay',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
