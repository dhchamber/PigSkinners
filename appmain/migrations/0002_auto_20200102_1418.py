# Generated by Django 3.0.1 on 2020-01-02 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Game',
        ),
        migrations.DeleteModel(
            name='Team',
        ),
    ]
