# Generated by Django 3.0.1 on 2020-01-10 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0033_auto_20200110_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='pick',
            name='koth_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='koth_team', to='appmain.Team'),
        ),
    ]
