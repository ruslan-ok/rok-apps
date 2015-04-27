# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_auto_20150406_2257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f'),
            preserve_default=True,
        ),
    ]
