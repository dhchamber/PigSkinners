# Generated by Django 3.0.1 on 2020-03-25 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0107_auto_20200321_0623'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='week',
            options={'ordering': ['year', 'id'], 'verbose_name': 'week', 'verbose_name_plural': 'weeks'},
        ),
    ]