# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0006_auto_20150406_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='active',
            field=models.IntegerField(default=0, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u0430\u044f'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='car',
            name='name',
            field=models.CharField(max_length=200, verbose_name='\u041c\u043e\u0434\u0435\u043b\u044c'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='car',
            name='plate',
            field=models.CharField(max_length=100, verbose_name='\u0413\u043e\u0441. \u043d\u043e\u043c\u0435\u0440'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuel',
            name='comment',
            field=models.CharField(max_length=1000, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuel',
            name='odometr',
            field=models.IntegerField(verbose_name='\u041f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u043e\u0434\u043e\u043c\u0435\u0442\u0440\u0430'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuel',
            name='price',
            field=models.DecimalField(verbose_name='\u0426\u0435\u043d\u0430', max_digits=15, decimal_places=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuel',
            name='volume',
            field=models.DecimalField(verbose_name='\u041e\u0431\u044a\u0451\u043c', max_digits=5, decimal_places=3),
            preserve_default=True,
        ),
    ]
