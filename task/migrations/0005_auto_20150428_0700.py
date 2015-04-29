# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_auto_20150427_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='active',
            field=models.IntegerField(default=0, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u0430'),
            preserve_default=True,
        ),
    ]
