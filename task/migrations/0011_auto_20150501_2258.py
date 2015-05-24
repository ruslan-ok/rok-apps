# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0010_auto_20150429_0333'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='code',
            field=models.CharField(max_length=200, verbose_name='\u041a\u043e\u0434', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='count',
            field=models.IntegerField(default=10, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u0438\u0439'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='cycle',
            field=models.IntegerField(default=0, verbose_name='\u0421\u043f\u043e\u0441\u043e\u0431 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u0438\u044f'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='done',
            field=models.IntegerField(default=0, verbose_name='\u0412\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u043e \u0440\u0430\u0437'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='repeat',
            field=models.IntegerField(default=0, verbose_name='\u041f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u0438\u0435'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='start',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='step',
            field=models.IntegerField(default=1, verbose_name='\u0428\u0430\u0433'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='stop',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='stop_mode',
            field=models.IntegerField(default=0, verbose_name='\u0421\u043f\u043e\u0441\u043e\u0431 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='value1',
            field=models.IntegerField(default=0, verbose_name='\u042d\u043b\u0435\u043c\u0435\u043d\u0442 \u043a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u044f 1'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='value2',
            field=models.IntegerField(default=0, verbose_name='\u042d\u043b\u0435\u043c\u0435\u043d\u0442 \u043a\u0430\u043b\u0435\u043d\u0434\u0430\u0440\u044f 2'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(null=True, verbose_name='\u0421\u0440\u043e\u043a \u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='pub_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f'),
            preserve_default=True,
        ),
    ]
