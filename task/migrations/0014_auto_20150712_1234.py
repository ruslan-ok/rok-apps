# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('task', '0013_remove_task_due_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('active', models.IntegerField(default=0, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u0430')),
                ('fltr', models.IntegerField(default=0, verbose_name='\u0424\u0438\u043b\u044c\u0442\u0440')),
                ('sort', models.IntegerField(default=0, verbose_name='\u0421\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0430')),
                ('grp', models.IntegerField(default=0, verbose_name='\u0413\u0440\u0443\u043f\u043f\u0438\u0440\u043e\u0432\u043a\u0430')),
                ('flds', models.IntegerField(default=0, verbose_name='\u041f\u043e\u043b\u044f')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='task',
            name='color',
            field=models.IntegerField(default=0, verbose_name='\u0410\u0442\u0440\u0438\u0431\u0443\u0442\u044b \u0437\u0430\u0434\u0430\u0447\u0438', blank=True),
            preserve_default=True,
        ),
    ]
