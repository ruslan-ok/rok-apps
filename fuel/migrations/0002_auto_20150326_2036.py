# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fuel',
            old_name='date',
            new_name='when',
        ),
        migrations.AlterField(
            model_name='fuel',
            name='comment',
            field=models.CharField(max_length=1000, blank=True),
            preserve_default=True,
        ),
    ]
