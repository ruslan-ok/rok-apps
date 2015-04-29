# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0009_auto_20150429_0308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='active',
            field=models.IntegerField(default=1, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u0430'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(default=datetime.date(2015, 4, 29), null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f', blank=True),
            preserve_default=True,
        ),
    ]
