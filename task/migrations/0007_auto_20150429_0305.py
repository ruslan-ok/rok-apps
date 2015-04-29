# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0006_auto_20150428_0702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='attrib',
            field=models.IntegerField(default=0, verbose_name='\u0410\u0442\u0440\u0438\u0431\u0443\u0442\u044b \u0437\u0430\u0434\u0430\u0447\u0438', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(default=datetime.date(2015, 1, 1), verbose_name='\u0412\u0440\u0435\u043c\u044f \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='grp',
            field=models.ForeignKey(default=1, blank=True, to='task.TGroup'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='pub_date',
            field=models.DateTimeField(default=datetime.date(2015, 4, 29), verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f'),
            preserve_default=True,
        ),
    ]
