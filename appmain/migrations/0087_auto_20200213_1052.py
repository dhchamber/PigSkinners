# Generated by Django 3.0.1 on 2020-02-13 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0086_auto_20200213_0714'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postpick',
            name='round_id',
        ),
        migrations.AlterField(
            model_name='postpick',
            name='points',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='postpickgame',
            name='ps_type',
            field=models.CharField(choices=[('AWC45', 'AFC Wild Card 45'), ('AWC36', 'AFC Wild Card 36'), ('ADIV1', 'AFC Divisional 1'), ('ADIV2', 'AFC Divisional 2'), ('ACONF', 'AFC Conference Champ'), ('NWC45', 'NFC Wild Card 45'), ('NWC36', 'NFC Wild Card 36'), ('NDIV1', 'NFC Divisional 1'), ('NDIV2', 'NFC Divisional 2'), ('NCONF', 'AFC Conference Champ'), ('SB', 'Super Bowl')], max_length=5),
        ),
    ]
