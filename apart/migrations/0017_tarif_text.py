# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0016_auto_20150408_2221'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarif',
            name='text',
            field=models.CharField(max_length=1000, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True),
            preserve_default=True,
        ),
    ]
