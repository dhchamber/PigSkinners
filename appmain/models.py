from django.conf import settings
from django.db import models
from django.utils import timezone

class Season(models.Model):
    year = models.PositiveSmallIntegerField
    start_date = models.DateField
    end_date = models.DateField

class Week(models.Model):
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    closed = models.BinaryField()
    closed_by = models.CharField(max_length=50)
    date_closed = models.DateTimeField(blank=True, null=True)
    actual_date_closed = models.DateTimeField(blank=True, null=True)
    forecast_date_closed = models.DateTimeField(blank=True, null=True)
    graphics_folder = models.CharField(max_length=100)
    standings_report_ran = models.BinaryField()
    weekly_standings_html = models.TextField()
    mobile_standings_report_ran = models.BinaryField()
    mobile_weekly_standings_html = models.TextField()

class Team(models.Model):
    team_name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)
    team_abrev = models.CharField(max_length=3)
    web_address = models.CharField(max_length=50)
    logo = models.CharField(max_length=50)
    division = models.CharField(max_length=50)
    logo_file_name = models.CharField(max_length=50)
    win = models.SmallIntegerField()
    lose = models.SmallIntegerField()
    tie = models.SmallIntegerField()
    conference = models.CharField(max_length=50)
    city_name = models.CharField(max_length=50)

class Game(models.Model):
    Year_id = models.PositiveSmallIntegerField()
    week = models.ForeignKey(Week,null=True,blank=True,on_delete=models.SET_NULL,related_name='week')
    game_number = models.PositiveSmallIntegerField()
    game_date = models.DateField()
    home_team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='home_team')
    visitor_team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='visitor_team')
    points_game = models.BinaryField()
    tv_network = models.CharField(max_length=10)
