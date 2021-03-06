# Generated by Django 3.0.1 on 2020-01-10 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0041_delete_season'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(default=2018)),
                ('active', models.BooleanField(default=False)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
            ],
        ),
    ]
