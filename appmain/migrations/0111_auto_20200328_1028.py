# Generated by Django 3.0.1 on 2020-03-28 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0110_auto_20200328_0728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pickrevision',
            name='revision',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
