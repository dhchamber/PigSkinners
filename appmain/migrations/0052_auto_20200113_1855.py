# Generated by Django 3.0.1 on 2020-01-14 01:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0051_game_home_teamname'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='visitor_name',
            new_name='visitor_nickname',
        ),
    ]
