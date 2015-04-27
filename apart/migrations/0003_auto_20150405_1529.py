# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0002_auto_20150405_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarif',
            name='month',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tarif',
            name='year',
            field=models.IntegerField(default=2000),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='resource',
            field=models.IntegerField(choices=[(1, '\u042d\u043b\u0435\u043a\u0442\u0440\u043e\u044d\u043d\u0435\u0440\u0433\u0438\u044f'), (2, '\u0413\u0430\u0437'), (3, '\u0412\u043e\u0434\u0430')]),
            preserve_default=True,
        ),
    ]
