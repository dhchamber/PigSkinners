# Generated by Django 3.0.1 on 2020-01-14 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0052_auto_20200113_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='visitor_teamname',
            field=models.CharField(default='a', max_length=20),
            preserve_default=False,
        ),
    ]
