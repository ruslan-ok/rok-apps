# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0011_auto_20150501_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='d_exec',
            field=models.DateField(null=True, verbose_name='\u0421\u0440\u043e\u043a \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f (\u0434\u0430\u0442\u0430)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='t_exec',
            field=models.TimeField(null=True, verbose_name='\u0421\u0440\u043e\u043a \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f (\u0432\u0440\u0435\u043c\u044f)', blank=True),
            preserve_default=True,
        ),
    ]
