# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0013_auto_20150406_2328'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarif',
            name='border2',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='\u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435 2'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tarif',
            name='border3',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='\u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435 3'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tarif',
            name='tarif2',
            field=models.DecimalField(default=0, verbose_name='\u0422\u0430\u0440\u0438\u0444 2', max_digits=15, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tarif',
            name='tarif3',
            field=models.DecimalField(default=0, verbose_name='\u0422\u0430\u0440\u0438\u0444 3', max_digits=15, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='border',
            field=models.DecimalField(null=True, verbose_name='\u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435 1', max_digits=15, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='tarif',
            field=models.DecimalField(verbose_name='\u0422\u0430\u0440\u0438\u0444 1', max_digits=15, decimal_places=3),
            preserve_default=True,
        ),
    ]
