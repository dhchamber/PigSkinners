# Generated by Django 3.0.1 on 2020-03-15 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0099_auto_20200313_1558'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='postpick',
            options={'ordering': ['year', 'user'], 'verbose_name': 'post season pick', 'verbose_name_plural': 'post season picks'},
        ),
        migrations.RemoveConstraint(
            model_name='postpick',
            name='ps_pick_user',
        ),
        migrations.RemoveIndex(
            model_name='postpick',
            name='appmain_pos_user_id_bdf5bb_idx',
        ),
        migrations.AddIndex(
            model_name='postpick',
            index=models.Index(fields=['year', 'user'], name='appmain_pos_year_id_b6f97f_idx'),
        ),
        migrations.AddConstraint(
            model_name='postpick',
            constraint=models.UniqueConstraint(fields=('year', 'user'), name='ps_pick_user'),
        ),
    ]