# Generated by Django 3.0.1 on 2020-01-10 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0021_auto_20200108_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nflgame',
            name='ga',
            field=models.CharField(max_length=2),
        ),
    ]
