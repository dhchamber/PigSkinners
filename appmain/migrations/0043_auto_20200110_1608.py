# Generated by Django 3.0.1 on 2020-01-10 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0042_season'),
    ]

    operations = [
        migrations.RenameField(
            model_name='season',
            old_name='active',
            new_name='current',
        ),
    ]
