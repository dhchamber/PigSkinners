# Generated by Django 3.0.1 on 2020-02-11 22:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0084_auto_20200211_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='seed',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gm_seeds', to='appmain.Game'),
        ),
    ]
