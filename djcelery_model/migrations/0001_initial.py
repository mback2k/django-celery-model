# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelTaskMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('task_id', models.CharField(unique=True, max_length=255)),
                ('state', models.PositiveIntegerField(default=0, choices=[(0, b'PENDING'), (1, b'STARTED'), (2, b'RETRY'), (3, b'FAILURE'), (4, b'SUCCESS')])),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
