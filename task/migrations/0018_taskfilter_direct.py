# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0017_auto_20151012_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskfilter',
            name='direct',
            field=models.IntegerField(default=0, verbose_name='\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0438'),
            preserve_default=True,
        ),
    ]
