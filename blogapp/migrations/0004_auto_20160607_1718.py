# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-07 11:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0003_auto_20160606_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='height_field',
        ),
        migrations.RemoveField(
            model_name='post',
            name='width_field',
        ),
    ]
