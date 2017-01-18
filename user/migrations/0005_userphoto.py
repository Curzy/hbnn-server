# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('image', models.ImageField(null=True, upload_to='')),
                ('priority', models.PositiveSmallIntegerField(default=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to='user.User')),
            ],
        ),
    ]
