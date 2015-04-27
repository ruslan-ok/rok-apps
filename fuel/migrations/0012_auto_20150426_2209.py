# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0011_part_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Repl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dt_chg', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u043c\u0435\u043d\u044b')),
                ('odometr', models.IntegerField(verbose_name='\u041f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u043e\u0434\u043e\u043c\u0435\u0442\u0440\u0430, \u043a\u043c')),
                ('manuf', models.CharField(max_length=1000, verbose_name='\u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c', blank=True)),
                ('part_num', models.CharField(max_length=100, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043f\u043e \u043a\u0430\u0442\u0430\u043b\u043e\u0433\u0443', blank=True)),
                ('name', models.CharField(max_length=1000, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('comment', models.TextField(verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True)),
                ('part', models.ForeignKey(to='fuel.Part')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='inspect',
            name='part',
        ),
        migrations.DeleteModel(
            name='Inspect',
        ),
    ]
