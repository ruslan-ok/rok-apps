# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0005_car_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuel',
            name='pub_date',
            field=models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u043f\u0440\u0430\u0432\u043a\u0438'),
            preserve_default=True,
        ),
    ]
