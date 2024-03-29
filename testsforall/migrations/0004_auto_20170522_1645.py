# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-22 16:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testsforall', '0003_auto_20170522_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='acceptDate',
            field=models.DateTimeField(help_text='Fecha de aceptaci\xf3n de amistad', null=True),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='daterequest',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 22, 16, 45, 22, 411117), help_text='Fecha de solicitud'),
        ),
        migrations.AlterField(
            model_name='usertests',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 22, 16, 45, 22, 408141), help_text='Fecha de creacion'),
        ),
    ]
