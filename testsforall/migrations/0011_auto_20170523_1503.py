# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-23 15:03
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testsforall', '0010_auto_20170523_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='daterequest',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 23, 15, 3, 9, 165269), help_text='Fecha de solicitud'),
        ),
        migrations.AlterField(
            model_name='result',
            name='score',
            field=models.FloatField(default=-1),
        ),
        migrations.AlterField(
            model_name='usertests',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 23, 15, 3, 9, 161383), help_text='Fecha de creacion'),
        ),
    ]