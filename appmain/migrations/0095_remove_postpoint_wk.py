# Generated by Django 3.0.1 on 2020-02-18 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0094_auto_20200218_0740'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postpoint',
            name='wk',
        ),
    ]
