# Generated by Django 3.0.1 on 2020-01-10 03:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0023_auto_20200109_2051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postresult',
            name='loser_team_id',
        ),
        migrations.RemoveField(
            model_name='postresult',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='postresult',
            name='winner_team_id',
        ),
        migrations.RemoveField(
            model_name='result',
            name='loser_team_id',
        ),
        migrations.RemoveField(
            model_name='result',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='result',
            name='winner_team_id',
        ),
        migrations.DeleteModel(
            name='PostPick',
        ),
        migrations.DeleteModel(
            name='PostResult',
        ),
        migrations.DeleteModel(
            name='Result',
        ),
    ]
