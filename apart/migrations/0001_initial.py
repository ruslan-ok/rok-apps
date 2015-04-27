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
            name='Communal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('state', models.IntegerField()),
                ('dCounter', models.DateTimeField()),
                ('dPay', models.DateTimeField()),
                ('el_old', models.DecimalField(max_digits=10, decimal_places=0)),
                ('el_new', models.DecimalField(max_digits=10, decimal_places=0)),
                ('el_pay', models.IntegerField()),
                ('tv_tar', models.IntegerField()),
                ('tv_pay', models.IntegerField()),
                ('phone_tar', models.IntegerField()),
                ('phone_pay', models.IntegerField()),
                ('zhirovka', models.IntegerField()),
                ('hot_pay', models.IntegerField()),
                ('repair_pay', models.IntegerField()),
                ('ZKX_pay', models.IntegerField()),
                ('cold_old', models.IntegerField()),
                ('cold_new', models.IntegerField()),
                ('hot_old', models.IntegerField()),
                ('hot_new', models.IntegerField()),
                ('water_pay', models.IntegerField()),
                ('gas_old', models.IntegerField()),
                ('gas_new', models.IntegerField()),
                ('gas_pay', models.IntegerField()),
                ('penalty', models.IntegerField()),
                ('prev_per', models.IntegerField()),
                ('course', models.IntegerField()),
                ('text', models.CharField(max_length=1000, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tarif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource', models.IntegerField()),
                ('attrib', models.IntegerField()),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('npp', models.IntegerField()),
                ('border', models.DecimalField(max_digits=15, decimal_places=3, blank=True)),
                ('tarif', models.DecimalField(max_digits=15, decimal_places=3)),
                ('user', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='communal',
            name='el_tar',
            field=models.ForeignKey(related_name='electro', to='apart.Tarif'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='communal',
            name='gas_tar',
            field=models.ForeignKey(related_name='gas', to='apart.Tarif'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='communal',
            name='user',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='communal',
            name='water_tar',
            field=models.ForeignKey(related_name='water', to='apart.Tarif'),
            preserve_default=True,
        ),
    ]
