# Generated by Django 3.0.1 on 2020-01-13 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0048_auto_20200113_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='week',
            name='gt',
            field=models.CharField(default='REG', max_length=3),
            preserve_default=False,
        ),
    ]
