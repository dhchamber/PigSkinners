# Generated by Django 3.0.1 on 2020-01-21 01:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0057_auto_20200118_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
