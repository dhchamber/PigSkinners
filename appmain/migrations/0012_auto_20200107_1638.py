# Generated by Django 3.0.1 on 2020-01-07 23:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0011_auto_20200105_1853'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='home_team_id',
            new_name='home_team',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='visitor_team_id',
            new_name='visitor_team',
        ),
    ]
