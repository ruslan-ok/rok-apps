# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='active',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u0430'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='attrib',
            field=models.IntegerField(verbose_name='\u0410\u0442\u0440\u0438\u0431\u0443\u0442\u044b \u0437\u0430\u0434\u0430\u0447\u0438'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='comment',
            field=models.CharField(max_length=2000, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(verbose_name='\u0412\u0440\u0435\u043c\u044f \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.CharField(max_length=200, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='pub_date',
            field=models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
