# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pir', '0002_auto_20150510_0327'),
    ]

    operations = [
        migrations.CreateModel(
            name='PirData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rec', models.CharField(max_length=1000, verbose_name='\u0417\u0430\u043f\u0438\u0441\u044c \u0442\u0430\u0431\u043b\u0438\u0446\u044b')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PirPart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u0411\u043b\u043e\u043a \u0434\u0430\u043d\u043d\u044b\u0445')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PirTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u0422\u0430\u0431\u043b\u0438\u0446\u0430')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pirpart',
            name='table',
            field=models.ForeignKey(to='pir.PirTable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pirdata',
            name='part',
            field=models.ForeignKey(default=1, to='pir.PirPart'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pirdata',
            name='table',
            field=models.ForeignKey(to='pir.PirTable'),
            preserve_default=True,
        ),
    ]
