# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0014_auto_20150408_2214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarif',
            name='border3',
        ),
    ]
