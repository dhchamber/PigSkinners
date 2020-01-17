from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.utils import timezone
from datetime import datetime
import pytz


class TimeStampMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
# TODO: change auto date fields, they are not using the right time zone

    class Meta:
        abstract = True


class Team(models.Model):
    team_name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)
    team_abrev = models.CharField(max_length=3)
    web_address = models.URLField(max_length=200)
    logo = models.CharField(max_length=50)
    division = models.CharField(max_length=50)
    logo_file_name = models.CharField(max_length=50)
    win = models.SmallIntegerField()
    lose = models.SmallIntegerField()
    tie = models.SmallIntegerField()
    conference = models.CharField(max_length=50)
    city_name = models.CharField(max_length=50)


class Profile(models.Model):
# additional user data
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=50,null=True)
    entry_fee = models.DecimalField(max_digits=6, decimal_places=2,default=0)
    ball_pool = models.BooleanField(default=False)
    king_hill_eligable = models.BooleanField(default=False)
# user updateable options
    intro_sound = models.BooleanField(default=False)
    show_graphics = models.BooleanField(default=False)
    show_video = models.BooleanField(default=False)
    favorite_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='favorite_team')
#    bio = models.TextField(max_length=500, blank=True)
#    location = models.CharField(max_length=30, blank=True)
#    birth_date = models.DateField(null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# TODO: this is probably not needed anymore
class Season(models.Model):
    yr = models.PositiveSmallIntegerField(null=True,default=2018)
    current = models.BooleanField(default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)


#TODO: start and end are not needed or can be compputed from Game model on the fly as min max of date/time
#TODO: as can forecast date closed, but maybe better to calc and store in table
class Week(models.Model):
    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL)    #? week of the season 1-17, 18-21
    week_no = models.PositiveSmallIntegerField(null=False) #? week of the season 1-17, 18-21  must be equal to id for foreign key
    gt = models.CharField(max_length=3) #game type?  REG = Regular Season(1-17); WC = Wild Card(18); DIV = Divisional(19); CON = Conference(20); SB = Super Bowl (22)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    closed_by = models.CharField(max_length=50,null=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    actual_date_closed = models.DateTimeField(blank=True, null=True)
    forecast_date_closed = models.DateTimeField(blank=True, null=True)
    graphics_folder = models.CharField(max_length=100,null=True)
    standings_report_ran = models.BooleanField(default=False)
    weekly_standings_html = models.TextField()
    mobile_standings_report_ran = models.BooleanField(default=False)
    mobile_weekly_standings_html = models.TextField()


class Game(TimeStampMixin):
    # Fields
    # from xml file gms header for each week
    gd = models.PositiveSmallIntegerField(null=True) #? always zero?
    week = models.ForeignKey(Week, null=True, blank=True, on_delete=models.SET_NULL, related_name='game_wk')    #key to ID in week table based on year and wk_no
    wk_no = models.PositiveSmallIntegerField(null=True)    #week of the NFL season 1-17, 18-20, 22
    year = models.PositiveSmallIntegerField(null=True) #? season year
    t = models.CharField(max_length=10, null=True) #? P = Post Season, R = Regular Season ?
    bf = models.CharField(max_length=10, null=True) #? 1?   from liveupdate postseason
    bph = models.CharField(max_length=10, null=True) #? 0? 172?  from liveupdate
    # from g record for each game
    eid = models.CharField(max_length=10) #date of game and count number
    gsis = models.CharField(max_length=10) #ID of game game key
    day = models.CharField(max_length=3) #day of the week of game
    time = models.CharField(max_length=5,null=True) #time of game in hh:mm format Eastern Time  TODO: convert to time data type
    status = models.CharField(max_length=3) #statue of game F= Finished; FO = Finished Overtime; P = Pending?;
    k = models.CharField(max_length=1, null=True) # ???
    home = models.CharField(max_length=3) #home team abreviation            HOU
    home_nickname = models.CharField(max_length=20,null=True) #home team nickname     texans
    home_teamname = models.CharField(max_length=20,null=True) #home team name         Houston Texans
    home_score = models.PositiveSmallIntegerField(null=True) #home team score
    visitor = models.CharField(max_length=3) #visitor team abreviation
    visitor_nickname = models.CharField(max_length=20,null=True) #visitor team nickname
    visitor_teamname = models.CharField(max_length=20,null=True) #visitor team nickname
    visitor_score = models.PositiveSmallIntegerField(null=True) #visitor team score
    p = models.CharField(max_length=1,null=True) # possession?
    red_zone = models.CharField(max_length=1,null=True) # ???
    ga = models.CharField(max_length=2,null=True) # ???
    gt = models.CharField(max_length=3,null=True) #game type?  REG = Regular Season(1-17); WC = Wild Card(18); DIV = Divisional(19); CON = Conference(20); SB = Super Bowl (22)

    # Metadata
    class Meta:
        ordering = ['gsis']

    def __str__(self):
        return self.gsis

    def get_date(self):
        year = self.eid[:4]
        mo = self.eid[4:6]
        day = self.eid[6:8]
        # date_str =  mo + '-' + day + '-' + year + ' ' + self.time[:2] + ':' + self.time[3:5] + ' PM'
        date_str =  mo + '-' + day + '-' + year + ' ' + self.time + ' PM'
        date_obj = datetime.strptime(date_str, '%m-%d-%Y %I:%M %p').astimezone(pytz.timezone('America/Los_Angeles'))
        return date_obj
# TODO: add methods to class for getting min and max date for week, projected close, ...


class Pick(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_user',default=1)
    wk = models.ForeignKey(Week, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_wk')    #? week of the season 1-17, 18-21
    points = models.PositiveSmallIntegerField()
    koth_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='koth_team')
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_updated')
    # date_entered = models.DateTimeField(default=datetime.now)
    # date_updated = models.DateTimeField(default=datetime.now)

class PickGame(models.Model):
    pick_head = models.ForeignKey(Pick,on_delete=models.CASCADE,related_name='pick_head')
    game = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='pick_game')
    team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='pick_team')  #team must be one of 2 teams in the game
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_game_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_game_updated')

# TODO: add method to determine if user has picked every game for a week  need to add a week ID to picks?

# TODO: Potential table for PostSeason seeds
# CREATE TABLE [dbo].[tblPostSeed](
# 	[PostSeedID] [int] IDENTITY(1,1) NOT NULL,
# 	[TeamID] [tinyint] NOT NULL,
# 	[Seed] [int] NOT NULL,

# TODO: Potential table for PostSeason points per round
# CREATE TABLE [dbo].[tblPostRound](
# 	[RoundID] [tinyint] NOT NULL,
# 	[Points] [int] NOT NULL,


# class Game(models.Model):  (from Pigskinners script)
#     Year_id = models.PositiveSmallIntegerField()
#     wk = models.ForeignKey(Week,null=True,blank=True,on_delete=models.SET_NULL,related_name='game_wk')
#     game_number = models.PositiveSmallIntegerField()
#     game_date = models.DateField()
#     home_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='home_team')
#     visitor_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='visitor_team')
#     points_game = models.BooleanField(default=False)
#     tv_network = models.CharField(max_length=10)

# class PostPick(models.Model):
#     round_id = models.PositiveSmallIntegerField()
#     user_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='post_team')
#     points = models.PositiveSmallIntegerField()

# class Result(models.Model):
#     schedule_id = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='result_game')
#     visitor_team_score = models.PositiveSmallIntegerField()
#     home_team_score = models.PositiveSmallIntegerField()
#     loser_team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='reuslt_loser')
#     winner_team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='result_winner')
#     tie = models.BinaryField()
#     updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     updated_time = models.DateTimeField(default=datetime.now)

# class PostResult(models.Model):
#     schedule_id = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='post_game')
#     visitor_team_score = models.PositiveSmallIntegerField()
#     home_team_score = models.PositiveSmallIntegerField()
#     loser_team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='post_loser')
#     winner_team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='post_winner')
#     tie = models.BinaryField()
#     updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     updated_time = models.DateTimeField(default=datetime.now)
