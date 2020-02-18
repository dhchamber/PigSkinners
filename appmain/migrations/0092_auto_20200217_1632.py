# Generated by Django 3.0.1 on 2020-02-17 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmain', '0091_postpick_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postpickgame',
            name='ps_type',
            field=models.CharField(choices=[('AWC45', 'AFC Wild Card 45'), ('NWC45', 'NFC Wild Card 45'), ('AWC36', 'AFC Wild Card 36'), ('NWC36', 'NFC Wild Card 36'), ('ADIV1', 'AFC Divisional 1'), ('ADIV2', 'AFC Divisional 2'), ('NDIV1', 'NFC Divisional 1'), ('NDIV2', 'NFC Divisional 2'), ('ACONF', 'AFC Conference Champ'), ('NCONF', 'AFC Conference Champ'), ('SB', 'Super Bowl')], default='AWC45', max_length=5),
        ),
    ]