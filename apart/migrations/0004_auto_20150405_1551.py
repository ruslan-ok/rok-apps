# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0003_auto_20150405_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarif',
            name='border',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=3, blank=True),
            preserve_default=True,
        ),
    ]
