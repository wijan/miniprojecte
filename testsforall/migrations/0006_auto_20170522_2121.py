# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-22 21:21
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testsforall', '0005_auto_20170522_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='daterequest',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 22, 21, 21, 37, 894588), help_text='Fecha de solicitud'),
        ),
        migrations.AlterField(
            model_name='usertests',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 22, 21, 21, 37, 892210), help_text='Fecha de creacion'),
        ),
    ]
