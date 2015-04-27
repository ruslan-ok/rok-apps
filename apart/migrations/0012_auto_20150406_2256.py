# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('apart', '0011_auto_20150406_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communal',
            name='ZKX_pay',
            field=models.IntegerField(verbose_name='\u0416\u041a\u0425 - \u043e\u043f\u043b\u0430\u0442\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='cold_new',
            field=models.IntegerField(verbose_name='\u0425\u043e\u043b\u043e\u0434\u043d\u0430\u044f \u0432\u043e\u0434\u0430 - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u043d\u043e\u0432\u044b\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='cold_old',
            field=models.IntegerField(verbose_name='\u0425\u043e\u043b\u043e\u0434\u043d\u0430\u044f \u0432\u043e\u0434\u0430 - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u0441\u0442\u0430\u0440\u044b\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='course',
            field=models.IntegerField(verbose_name='\u041a\u0443\u0440\u0441 \u0434\u043e\u043b\u043b\u0430\u0440\u0430 \u043d\u0430 \u0434\u0430\u0442\u0443 \u043e\u043f\u043b\u0430\u0442\u044b', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='dCounter',
            field=models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043d\u044f\u0442\u0438\u044f \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u0439 \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='dPay',
            field=models.DateTimeField(verbose_name='\u0414\u0430\u0442\u0430 \u043e\u043f\u043b\u0430\u0442\u044b'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='el_new',
            field=models.IntegerField(verbose_name='\u042d\u043b\u0435\u043a\u0442\u0440\u043e\u044d\u043d\u0435\u0440\u0433\u0438\u044f - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u043d\u043e\u0432\u044b\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='el_old',
            field=models.IntegerField(verbose_name='\u042d\u043b\u0435\u043a\u0442\u0440\u043e\u044d\u043d\u0435\u0440\u0433\u0438\u044f - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u0441\u0442\u0430\u0440\u044b\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='el_pay',
            field=models.IntegerField(verbose_name='\u042d\u043b\u0435\u043a\u0442\u0440\u043e\u044d\u043d\u0435\u0440\u0433\u0438\u044f - \u043e\u043f\u043b\u0430\u0447\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='gas_new',
            field=models.IntegerField(verbose_name='\u0413\u0430\u0437 - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u043d\u043e\u0432\u044b\u0435 ', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='gas_old',
            field=models.IntegerField(verbose_name='\u0413\u0430\u0437 - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u0441\u0442\u0430\u0440\u044b\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='gas_pay',
            field=models.IntegerField(verbose_name='\u0413\u0430\u0437 - \u043e\u043f\u043b\u0430\u0447\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='hot_new',
            field=models.IntegerField(verbose_name='\u0413\u043e\u0440\u044f\u0447\u0430\u044f \u0432\u043e\u0434\u0430 - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u043d\u043e\u0432\u044b\u0435 ', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='hot_old',
            field=models.IntegerField(verbose_name='\u0413\u043e\u0440\u044f\u0447\u0430\u044f \u0432\u043e\u0434\u0430 - \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0438\u044f \u0441\u0447\u0435\u0442\u0447\u0438\u043a\u0430 \u0441\u0442\u0430\u0440\u044b\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='hot_pay',
            field=models.IntegerField(verbose_name='\u0422\u0435\u043f\u043b\u043e\u044d\u043d\u0435\u0440\u0433\u0438\u044f - \u043e\u043f\u043b\u0430\u0442\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='month',
            field=models.IntegerField(verbose_name='\u041c\u0435\u0441\u044f\u0446'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='penalty',
            field=models.IntegerField(verbose_name='\u041f\u0435\u043d\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='period',
            field=models.IntegerField(verbose_name='\u041e\u0442\u0447\u0435\u0442\u043d\u044b\u0439 \u043f\u0435\u0440\u0438\u043e\u0434'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='phone_pay',
            field=models.IntegerField(verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d - \u043e\u043f\u043b\u0430\u0447\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='phone_tar',
            field=models.IntegerField(verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d - \u043d\u0430\u0447\u0438\u0441\u043b\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='prev_per',
            field=models.IntegerField(verbose_name='\u041f\u0440\u0435\u0434\u044b\u0434\u0443\u0449\u0438\u0439 \u043f\u0435\u0440\u0438\u043e\u0434', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='repair_pay',
            field=models.IntegerField(verbose_name='\u041a\u0430\u043f\u0440\u0435\u043c\u043e\u043d\u0442 - \u043e\u043f\u043b\u0430\u0442\u0430', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='state',
            field=models.IntegerField(verbose_name='\u0421\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='text',
            field=models.CharField(max_length=1000, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='tv_pay',
            field=models.IntegerField(verbose_name='\u0413\u043e\u0440\u0430\u0442\u043e\u0440\u0433 - \u043e\u043f\u043b\u0430\u0447\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='tv_tar',
            field=models.IntegerField(verbose_name='\u0413\u043e\u0440\u0430\u0442\u043e\u0440\u0433 - \u043d\u0430\u0447\u0438\u0441\u043b\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='water_pay',
            field=models.IntegerField(verbose_name='\u0412\u043e\u0434\u0430 - \u043e\u043f\u043b\u0430\u0447\u0435\u043d\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='year',
            field=models.IntegerField(verbose_name='\u0413\u043e\u0434'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='communal',
            name='zhirovka',
            field=models.IntegerField(verbose_name='\u0421\u0443\u043c\u043c\u0430 \u0438\u0437 \u0436\u0438\u0440\u043e\u0432\u043a\u0438', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='attrib',
            field=models.IntegerField(verbose_name='\u0410\u0442\u0440\u0438\u0431\u0443\u0442\u044b', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='border',
            field=models.DecimalField(null=True, verbose_name='\u041e\u0433\u0440\u0430\u043d\u0438\u0447\u0435\u043d\u0438\u0435', max_digits=15, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='month',
            field=models.IntegerField(verbose_name='\u041c\u0435\u0441\u044f\u0446'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='npp',
            field=models.IntegerField(verbose_name='\u041d\u043e\u043c\u0435\u0440 \u043f\u043e \u043f\u043e\u0440\u044f\u0434\u043a\u0443'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='period',
            field=models.IntegerField(verbose_name='\u041e\u0442\u0447\u0435\u0442\u043d\u044b\u0439 \u043f\u0435\u0440\u0438\u043e\u0434'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='resource',
            field=models.IntegerField(verbose_name='\u0422\u0438\u043f \u0440\u0435\u0441\u0443\u0440\u0441\u0430', choices=[(1, '\u042d\u043b\u0435\u043a\u0442\u0440\u043e\u044d\u043d\u0435\u0440\u0433\u0438\u044f'), (2, '\u0413\u0430\u0437'), (3, '\u0412\u043e\u0434\u0430')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='tarif',
            field=models.DecimalField(verbose_name='\u0422\u0430\u0440\u0438\u0444', max_digits=15, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tarif',
            name='year',
            field=models.IntegerField(verbose_name='\u0413\u043e\u0434'),
            preserve_default=True,
        ),
    ]
