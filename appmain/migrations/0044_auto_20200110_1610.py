# Generated by Django 3.0.1 on 2020-01-10 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0043_auto_20200110_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='year',
            field=models.PositiveSmallIntegerField(default=2018, null=True),
        ),
    ]
