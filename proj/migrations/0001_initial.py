# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Direct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435')),
                ('active', models.IntegerField(default=0, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u043e\u0435')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proj',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0438')),
                ('kol', models.DecimalField(max_digits=15, decimal_places=3)),
                ('price', models.IntegerField()),
                ('course', models.IntegerField()),
                ('usd', models.IntegerField()),
                ('kontr', models.CharField(max_length=1000, blank=True)),
                ('text', models.CharField(max_length=1000, blank=True)),
                ('direct', models.ForeignKey(to='proj.Direct')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
