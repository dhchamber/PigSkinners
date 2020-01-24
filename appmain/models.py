from django.db import models
from django.db.models import Max, Min
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
import pytz


class TimeStampMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
# TODO: change auto date fields, they are not using the right time zone

    class Meta:
        abstract = True


# must be defined before Profile because it is referenced in favorite team
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

    def __str__(self):
        return self.team_name


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


class Season(models.Model):
    yr = models.PositiveSmallIntegerField(null=True,default=2018)
    current = models.BooleanField(default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return str(self.yr)


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

    def __str__(self):
        return str(self.week_no) + '/' + self.gt

    def date_range(self):
        min_date = self.game_wk.aggregate(mind=Min('date_time'))['mind']
        max_date = self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']
        print(f'{min_date.strftime("%m-%d-%Y")} to {max_date.strftime("%m-%d-%Y")}')
        return min_date.strftime('%m-%d-%Y') + ' to ' + max_date.strftime('%m-%d-%Y')


# TODO: add methods to class for getting min and max date for week, projected close, ...

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
    date_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=3) #statue of game F= Finished; FO = Finished Overtime; P = Pending?;
    k = models.CharField(max_length=1, null=True) # ???
    home_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name='home')
    home = models.CharField(max_length=3) #home team abreviation            HOU
    home_nickname = models.CharField(max_length=20,null=True) #home team nickname     texans
    home_teamname = models.CharField(max_length=20,null=True) #home team name         Houston Texans
    home_score = models.PositiveSmallIntegerField(null=True) #home team score
    visitor_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name='visitor')
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
        # the time of the game from the game feed is in Eastern time, convert to Mountain
        est = pytz.timezone('America/New_York')
        year = int(self.eid[:4])
        mo = int(self.eid[4:6])
        day = int(self.eid[6:8])
        hour, min = self.time.split(':')
        # print(f'{self.gsis} year: {year} mo: {mo} day: {day} t: hour: {hour} min: {min}')
        # print(f'{self.gsis} year: {year} mo: {mo} day: {day} t: hour: {int(hour)+12} min: {min}')
        est_date = make_aware(datetime(year,mo,day,int(hour)+12,int(min)), pytz.timezone('America/New_York'))
        mst_date = est_date.astimezone(pytz.timezone('America/Denver'))  #conver date to MST
        return mst_date

    def win_team(self):
        if self.home_score > self.visitor_score:
            return self.home_team
        elif self.home_score < self.visitor_score:
            return self.visitor_team
        else:
            pass

    def lose_team(self):
        if self.home_score > self.visitor_score:
            return self.visitor_team
        elif self.home_score < self.visitor_score:
            return self.home_team
        else:
            pass

    def game_winner(self):
        if self.status == 'F' or self.status == 'FO':
            if self.home_score > self.visitor_score:
                return self.home_team
            elif self.home_score < self.visitor_score:
                return self.visitor_team
            elif self.home_score == self.visitor_score:
                return 'Tie'
            else:
                return 'Error'


class Pick(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_user',default=1)
    wk = models.ForeignKey(Week, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_wk')
    points = models.PositiveSmallIntegerField()
    koth_game = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='koth_game')
    koth_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='koth_team')
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_updated')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','wk'], name='pick_user_wk')]

    def pick_year(self):
        return self.wk.year

    def koth_eligible(self):
        curr_yr = Season.objects.get(current=True)
        curr_wks = Week.objects.filter(year=curr_yr)
        user_picks = Pick.objects.filter(user=self.user, wk__in=curr_wks)
        eligible = True
        for pick in user_picks:
            if pick.koth_game:
                if pick.koth_game.lose_team() == self.koth_team:
                    eligible = False
                    break

        return eligible

    # def cap_user(self):
    #     return self.user.capitalize()

    # only allow teams that have games this week in the list
    # get Home teams, visitors, teams already used
    # take union and then difference
    def koth_remaining(self):
        curr_yr = Season.objects.get(current=True)
        games = Game.objects.filter(week=self.wk)
        curr_wks = Week.objects.filter(year=curr_yr)
        used_picks = Pick.objects.filter(user=self.user, wk__in=curr_wks).values_list('koth_team',flat=True)
        teams = []
        for game in games:
            if game.home_team.id not in used_picks:
                teams.append(game.home_team)
            if game.visitor_team.id not in used_picks:
                teams.append(game.visitor_team)

        return teams


class PickGame(models.Model):
    pick_head = models.ForeignKey(Pick,on_delete=models.CASCADE)  # ,related_name='pick_head'
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
