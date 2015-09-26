# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0014_auto_20150712_1234'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity', models.IntegerField(default=0, verbose_name='\u0421\u0443\u0449\u043d\u043e\u0441\u0442\u044c')),
                ('npp', models.IntegerField(default=0, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043f\u043e \u043f\u043e\u0440\u044f\u0434\u043a\u0443')),
                ('value', models.IntegerField(default=0, verbose_name='\u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435')),
                ('view', models.ForeignKey(to='task.TaskView')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
