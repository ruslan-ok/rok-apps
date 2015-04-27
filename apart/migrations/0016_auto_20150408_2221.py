# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0015_remove_tarif_border3'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarif',
            name='npp',
        ),
        migrations.AlterField(
            model_name='tarif',
            name='border',
            field=models.DecimalField(null=True, verbose_name='\u0413\u0440\u0430\u043d\u0438\u0446\u0430 1', max_digits=15, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='border2',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='\u0413\u0440\u0430\u043d\u0438\u0446\u0430 2'),
            preserve_default=True,
        ),
    ]
