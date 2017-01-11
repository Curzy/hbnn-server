# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-11 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20170110_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.SmallIntegerField(choices=[(1, '남'), (2, '여')], default=1),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=60, unique=True),
        ),
    ]
