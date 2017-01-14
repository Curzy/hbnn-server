# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-14 07:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20170112_0209'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taste', models.SmallIntegerField(choices=[(1, '한식'), (2, '중식'), (3, '일식'), (4, '양식'), (5, '채식')])),
                ('introduction', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
        ),
    ]
