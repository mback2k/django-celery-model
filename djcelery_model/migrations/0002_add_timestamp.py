# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery_model', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ModelTaskMeta',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ModelTaskMeta',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
