# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-18 13:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('envelopes', '0002_auto_20151110_1319'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='envelopes',
            options={'ordering': ['name', 'cash'], 'verbose_name': '\u043a\u043e\u043d\u0432\u0435\u0440\u0442', 'verbose_name_plural': '\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u044b'},
        ),
        migrations.AlterField(
            model_name='envelopes',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='general.Accounts'),
        ),
    ]
