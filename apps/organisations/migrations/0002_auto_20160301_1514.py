# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.
# Generated by Django 1.9.1 on 2016-03-01 15:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organisation',
            options={'ordering': ['name']},
        ),
    ]
