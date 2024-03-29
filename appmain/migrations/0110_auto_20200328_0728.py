# Generated by Django 3.0.1 on 2020-03-28 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appmain', '0109_auto_20200328_0724'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickRevGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=1, null=True)),
            ],
            options={
                'verbose_name': 'pick game',
                'verbose_name_plural': 'pick games',
            },
        ),
        migrations.RemoveConstraint(
            model_name='pick',
            name='pick_uweser_wk',
        ),
        migrations.AddConstraint(
            model_name='pick',
            constraint=models.UniqueConstraint(fields=('user', 'wk'), name='pick_user_wk'),
        ),
        migrations.AddField(
            model_name='pickrevgame',
            name='entered_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pick_rev_game_entered', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pickrevgame',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pick_rev_game', to='appmain.Game'),
        ),
        migrations.AddField(
            model_name='pickrevgame',
            name='pickrev_head',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appmain.PickRevision'),
        ),
        migrations.AddField(
            model_name='pickrevgame',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pick_rev_team', to='appmain.Team'),
        ),
        migrations.AddField(
            model_name='pickrevgame',
            name='updated_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pick_rev_game_updated', to=settings.AUTH_USER_MODEL),
        ),
    ]
