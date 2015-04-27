# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0003_auto_20150326_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuel',
            name='pub_date',
            field=models.DateTimeField(verbose_name=b'date published'),
            preserve_default=True,
        ),
    ]
