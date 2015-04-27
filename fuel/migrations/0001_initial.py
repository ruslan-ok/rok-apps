# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('plate', models.SlugField()),
                ('active', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fuel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('odometr', models.IntegerField()),
                ('volume', models.DecimalField(max_digits=5, decimal_places=3)),
                ('price', models.DecimalField(max_digits=15, decimal_places=0)),
                ('comment', models.CharField(max_length=1000)),
                ('car', models.ForeignKey(to='fuel.Car')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
