# Generated by Django 3.0.1 on 2020-01-13 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0047_week_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='week',
            name='year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appmain.Season'),
        ),
    ]
