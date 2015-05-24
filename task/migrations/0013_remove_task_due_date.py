# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0012_auto_20150509_2318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='due_date',
        ),
    ]
