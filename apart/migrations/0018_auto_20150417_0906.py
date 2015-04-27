# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0017_tarif_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarif',
            name='resource',
            field=models.IntegerField(verbose_name='\u0422\u0438\u043f \u0440\u0435\u0441\u0443\u0440\u0441\u0430', choices=[(1, '\u044d\u043b\u0435\u043a\u0442\u0440\u043e'), (2, '\u0433\u0430\u0437'), (3, '\u0432\u043e\u0434\u0430')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='tarif2',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='\u0422\u0430\u0440\u0438\u0444 2'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='tarif3',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=15, blank=True, null=True, verbose_name='\u0422\u0430\u0440\u0438\u0444 3'),
            preserve_default=True,
        ),
    ]
