# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-09-14 11:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0002_address'),
        ('users', '0003_user_email_actice'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='default_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='addresses.Address'),
        ),
    ]
