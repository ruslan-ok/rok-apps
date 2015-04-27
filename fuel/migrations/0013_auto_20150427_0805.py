# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proj', '0002_auto_20150419_0714'),
        ('fuel', '0012_auto_20150426_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='direct',
            field=models.ForeignKey(to='proj.Direct', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='repl',
            name='oper',
            field=models.ForeignKey(to='proj.Proj', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='repl',
            name='comment',
            field=models.TextField(default=None, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True),
            preserve_default=True,
        ),
    ]
