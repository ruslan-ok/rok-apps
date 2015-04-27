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
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('comment', models.CharField(max_length=2000, blank=True)),
                ('pub_date', models.DateTimeField(verbose_name=b'date published')),
                ('due_date', models.DateTimeField(verbose_name=b'event time')),
                ('active', models.PositiveSmallIntegerField(default=0)),
                ('attrib', models.IntegerField()),
                ('user', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
