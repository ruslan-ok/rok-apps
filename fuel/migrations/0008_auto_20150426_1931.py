# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fuel', '0007_auto_20150411_1913'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dt_chg', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0437\u0430\u043c\u0435\u043d\u044b')),
                ('odometr', models.IntegerField(verbose_name='\u041f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u043e\u0434\u043e\u043c\u0435\u0442\u0440\u0430, \u043a\u043c')),
                ('manuf', models.CharField(max_length=1000, verbose_name='\u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c', blank=True)),
                ('part_num', models.CharField(max_length=100, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043f\u043e \u043a\u0430\u0442\u0430\u043b\u043e\u0433\u0443', blank=True)),
                ('name', models.CharField(max_length=1000, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435', blank=True)),
                ('comment', models.TextField(verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AutoMaterial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1000, verbose_name='\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435')),
                ('chg_km', models.IntegerField(verbose_name='\u0418\u043d\u0442\u0435\u0440\u0432\u0430\u043b \u0437\u0430\u043c\u0435\u043d\u044b, \u043a\u043c', blank=True)),
                ('chg_mo', models.IntegerField(verbose_name='\u0418\u043d\u0442\u0435\u0440\u0432\u0430\u043b \u0437\u0430\u043c\u0435\u043d\u044b, \u043c\u0435\u0441\u044f\u0446\u0435\u0432', blank=True)),
                ('last_km', models.IntegerField(verbose_name='\u041f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u043e\u0434\u043e\u043c\u0435\u0442\u0440\u0430 \u043f\u0440\u0438 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0439 \u0437\u0430\u043c\u0435\u043d\u0435, \u043a\u043c', blank=True)),
                ('last_mo', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u0439 \u0437\u0430\u043c\u0435\u043d\u044b', blank=True)),
                ('car', models.ForeignKey(to='fuel.Car')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='autochange',
            name='material',
            field=models.ForeignKey(to='fuel.AutoMaterial'),
            preserve_default=True,
        ),
    ]
