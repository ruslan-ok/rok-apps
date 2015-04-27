# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_auto_20150427_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='attrib',
            field=models.IntegerField(default=0, verbose_name='\u0410\u0442\u0440\u0438\u0431\u0443\u0442\u044b \u0437\u0430\u0434\u0430\u0447\u0438'),
            preserve_default=True,
        ),
    ]
