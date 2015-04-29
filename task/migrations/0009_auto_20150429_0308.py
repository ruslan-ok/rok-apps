# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0008_auto_20150429_0307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='grp',
            field=models.ForeignKey(blank=True, to='task.TGroup', null=True),
            preserve_default=True,
        ),
    ]
