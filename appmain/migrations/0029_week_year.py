# Generated by Django 3.0.1 on 2020-01-10 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0028_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='week',
            name='year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='week_yr', to='appmain.Season'),
        ),
    ]
