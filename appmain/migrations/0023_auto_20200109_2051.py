# Generated by Django 3.0.1 on 2020-01-10 03:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0022_auto_20200109_1804'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postresult',
            name='schedule_id',
        ),
        migrations.RemoveField(
            model_name='result',
            name='schedule_id',
        ),
    ]
