# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0015_taskfilter'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskview',
            name='code',
            field=models.CharField(default=b'', max_length=200, verbose_name='\u041a\u043e\u0434 \u0434\u043b\u044f \u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0438'),
            preserve_default=True,
        ),
    ]
