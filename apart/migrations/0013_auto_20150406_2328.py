# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0012_auto_20150406_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communal',
            name='dCounter',
            field=models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043d\u044f\u0442\u0438\u044f \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u0439 \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='dPay',
            field=models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043f\u043b\u0430\u0442\u044b', blank=True),
            preserve_default=True,
        ),
    ]
