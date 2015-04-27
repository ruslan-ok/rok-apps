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
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('dative', models.CharField(max_length=500)),
                ('me', models.IntegerField()),
                ('user', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Saldo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('me', models.IntegerField()),
                ('summ', models.IntegerField()),
                ('p1', models.ForeignKey(related_name='p1', to='trip.Person')),
                ('p2', models.ForeignKey(related_name='p2', to='trip.Person')),
                ('user', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('year', models.IntegerField()),
                ('week', models.IntegerField()),
                ('days', models.IntegerField()),
                ('oper', models.IntegerField()),
                ('price', models.IntegerField()),
                ('text', models.CharField(max_length=1000, blank=True)),
                ('driver', models.ForeignKey(related_name='driver', to='trip.Person')),
                ('passenger', models.ForeignKey(related_name='passenger', to='trip.Person')),
                ('user', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
