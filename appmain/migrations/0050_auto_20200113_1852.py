# Generated by Django 3.0.1 on 2020-01-14 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0049_week_gt'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='home_name',
            new_name='home_nickname',
        ),
        migrations.AddField(
            model_name='game',
            name='bph',
            field=models.CharField(default='a', max_length=10),
            preserve_default=False,
        ),
    ]
