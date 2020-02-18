from django.db import models
from django.db.models import Max, Min
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
import pytz
from datetime import datetime, timedelta
from django.utils import timezone
from enum import Enum

class TimeStampMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
# TODO: change auto date fields, they are not using the right time zone

    class Meta:
        abstract = True


# must be defined before Profile because it is referenced in favorite team
class Team(models.Model):
    class Meta:
        verbose_name = 'team'
        verbose_name_plural = 'teams'
        indexes = [models.Index(fields=['team_abrev','short_name'])]
        ordering = ['team_abrev']

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

    def cy_seed(self):
        seed = Seed.objects.get(team=self,year=Season.objects.get(current=True))
        return seed


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
    class Meta:
        verbose_name = 'season'
        verbose_name_plural = 'seasons'
        indexes = [models.Index(fields=['year','current'])]
        ordering = ['year']

    year = models.PositiveSmallIntegerField(null=False, default=2020)
    current = models.BooleanField(null=False, default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return str(self.year)

    # def get_absolute_url(self):
    #     return reverse('season_detail',args=[str(self.id)])

    # def start_dt(self):
    #     return self.game_wk.aggregate(mind=Min('date_time'))['mind']
    #
    # def end_dt(self):
    #     return self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']

#TODO: start and end are not needed or can be compputed from Game model on the fly as min max of date/time
#TODO: as can forecast date closed, but maybe better to calc and store in table
class Week(models.Model):
    class Meta:
        verbose_name = 'week'
        verbose_name_plural = 'weeks'
        indexes = [models.Index(fields=['year','week_no','gt','closed'])]
        ordering = ['year','week_no']

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL)
    week_no = models.PositiveSmallIntegerField(null=False) #? week of the season 1-17, 18-21  must be equal to id for foreign key
#TODO: need a way to sort correctly be week and week type, add new model for gt with key 1,2,3 ??
    gt = models.CharField(max_length=3) #game type  REG = Regular Season(1-17); WC = Wild Card(18); DIV = Divisional(19); CON = Conference(20); SB = Super Bowl (22)
    closed = models.BooleanField(default=False)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL,default=1)  #models.CharField(max_length=50,null=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    actual_date_closed = models.DateTimeField(blank=True, null=True)
    graphics_folder = models.CharField(max_length=100,null=True,blank=True)
    standings_report_ran = models.BooleanField(default=False)
    weekly_standings_html = models.TextField(blank=True)
    mobile_standings_report_ran = models.BooleanField(default=False)
    mobile_weekly_standings_html = models.TextField(blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    forecast_date_closed = models.DateField(null=True,blank=True)

    def __str__(self):
        return str(self.week_no) + '/' + self.gt

    def start_dt(self):
        return self.game_wk.aggregate(mind=Min('date_time'))['mind']

    def end_dt(self):
        return self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']

    def forecast_dt_closed(self):
        if self.start_dt():
            return self.start_dt() - timedelta(hours=2)

#TODO: if day = day then just return the first day
    def postseason_week(self):
        timezone.activate(pytz.timezone('America/Denver'))
        min_date = self.game_wk.aggregate(mind=Min('date_time'))['mind']
        max_date = self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']

        if min_date.strftime("%d") == max_date.strftime("%d"):
            date_str = min_date.strftime("%b. %d")
        else:
            date_str = min_date.strftime("%b. %d") + '-' + max_date.strftime("%d")
        return date_str

    # get current time (in UTC timezone) if after forecast close (which is alos in UTC) then close the week
    def close_week(self, user):
        if self.start_dt():
            if timezone.now() > self.forecast_dt_closed():
                self.closed = True
                self.date_closed = timezone.now()
                self.closed_by = user
                self.save()
                return True
        return False

    #TODO: date range returns dates in UTC date/time  when truncated to date it is wrong when displayed on picks page
    #TODO: remove, not needed anymore
    # def date_range(self):
    #     min_date = self.game_wk.aggregate(mind=Min('date_time'))['mind']
    #     max_date = self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']
    #     print(f'{min_date.strftime("%m-%d-%Y")} to {max_date.strftime("%m-%d-%Y")}')
    #     return min_date.strftime('%m-%d-%Y') + ' to ' + max_date.strftime('%m-%d-%Y')


class Game(TimeStampMixin):
    class Meta:
        verbose_name = 'game'
        verbose_name_plural = 'games'
        indexes = [models.Index(fields=['week','year','eid','gsis'])]
        ordering = ['gsis']

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
    winner = models.ForeignKey(Team,null=True, blank=True, on_delete=models.SET_NULL,related_name='wins')
    p = models.CharField(max_length=1,null=True) # possession
    network = models.CharField(max_length=20,null=True)
    red_zone = models.CharField(max_length=1,null=True) # ???
    ga = models.CharField(max_length=2,null=True) # ???
    gt = models.CharField(max_length=3,null=True) #game type?  REG = Regular Season(1-17); WC = Wild Card(18); DIV = Divisional(19); CON = Conference(20); SB = Super Bowl (22)
    points_game = models.BooleanField(default=False)

    def __str__(self):
        return self.gsis

    def points_score(self):
        return self.home_score + self.visitor_score

    def get_date(self):
        # the time of the game from the game feed is in Eastern time, convert to Mountain
        est = pytz.timezone('America/New_York')
        year = int(self.eid[:4])
        mo = int(self.eid[4:6])
        day = int(self.eid[6:8])
        hour, min = self.time.split(':')
        # print(f'{self.gsis} year: {year} mo: {mo} day: {day} t: hour: {hour} min: {min}')
        # print(f'{self.gsis} year: {year} mo: {mo} day: {day} t: hour: {int(hour)+12} min: {min}')
#TODO: there is a problem with some times in week 13  need to handle this
        if int(hour) < 12:
            est_date = make_aware(datetime(year,mo,day,int(hour)+12,int(min)), pytz.timezone('America/New_York'))
        else:
            est_date = make_aware(datetime(year, mo, day, int(hour), int(min)), pytz.timezone('America/New_York'))
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

    def tie(self):
        if self.home_score == self.visitor_score:
            return True
        else:
            return False

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

#  Table for PostSeason seeds
class Seed(models.Model):
    class Meta:
        verbose_name = 'seed'
        verbose_name_plural = 'seeds'
        indexes = [models.Index(fields=['year', 'team'])]
        ordering = ['year', 'team','seed']
        constraints = [models.UniqueConstraint(fields=['year', 'team'], name='year_team')]

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='seeds')
    game = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='gm_seeds')
    seed = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.seed)

class PickManager(models.Manager):
    def create_pick(self, user, week):
        pick = self.create(user=user, wk=week, points=0, entered_by=user, updated_by=user)
        for game in Game.objects.filter(week=week):
            game_picks = PickGame.objects.create(pick_head=pick, game=game, entered_by=user,updated_by=user)
            game_picks.save()
        pick.save()
        return pick

# add manager for picks in current year
class Pick(models.Model):
    class Meta:
        verbose_name = 'pick'
        verbose_name_plural = 'picks'
        indexes = [models.Index(fields=['user','wk'])]
        ordering = ['user','wk']
        constraints = [models.UniqueConstraint(fields=['user','wk'], name='pick_user_wk')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='picks',default=1)
    wk = models.ForeignKey(Week, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_wk')
    points = models.PositiveSmallIntegerField()
    koth_game = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='koth_game')
    koth_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='koth_team')
    pick_score = models.PositiveSmallIntegerField(default=0)
    saved = models.BooleanField(default=False)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_updated')

    objects = PickManager()

    # TODO: add method to determine if user has picked every game for a week

    # create a new pick for a user for the week and create records for all the games in the week
    # @classmethod
    # def create(cls, user, week):
    #     pick = cls(user=user, wk=week)
    #     for game in Game.objects.filter(week=week):
    #         game_picks = PickGame.objects.create(pick_head=pick, game=game, entered_by=user,updated_by=user)
    #         game_picks.save()
    #     return cls

    def pick_year(self):
        return self.wk.year

    def koth_eligible(self):
        curr_yr = Season.objects.get(current=True)
        curr_wks = Week.objects.filter(year=curr_yr, closed=True)
        user_picks = Pick.objects.filter(user=self.user, wk__in=curr_wks)
        eligible = True
        for pick in user_picks:
            if pick.koth_game:
                if pick.koth_game.lose_team() == self.koth_team:
                    eligible = False
                    break

        return eligible

    # return 1 if user won KOTH game, 0 if lost or tied
    def koth_score(self):
        if self.koth_game.win_team() == self.koth_team:
            return 1
        else:
            return 0

    def koth_remaining(self):
        curr_yr = Season.objects.get(current=True)
        games = Game.objects.filter(week=self.wk)
        curr_wks = Week.objects.filter(year=curr_yr, closed=True)
        used_picks = Pick.objects.filter(user=self.user, wk__in=curr_wks).values_list('koth_team',flat=True)
        teams = []
        for game in games:
            if game.home_team.id not in used_picks:
                teams.append(game.home_team)
            if game.visitor_team.id not in used_picks:
                teams.append(game.visitor_team)

        return teams

    def calc_score(self):
        sum_score = 0
        for pg in self.pickgame_set.all():
            sum_score += pg.pick_score()

        return sum_score

    def cap_user(self):
        return self.user.capitalize()


class PickGame(models.Model):
    class Meta:
        verbose_name = 'pick game'
        verbose_name_plural = 'pick games'

    pick_head = models.ForeignKey(Pick,on_delete=models.CASCADE)  # ,related_name='pick_head'
    game = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='pick_game')
    team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='pick_team')  #team must be one of 2 teams in the game
    status = models.CharField(max_length=1, null=True)  # W = won, w= Pending win, L = Lost, l= pending loss, T= Tie, t=pending tie
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_game_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='pick_game_updated')

    # return 1 if user won the game, 0 if lost or tied
    def pick_score(self):
        if self.game.win_team() == self.team:
            return 1
        else:
            return 0


class PostPickManager(models.Manager):
    def create_ps_pick(self, user):
        pick = self.create(user=user, entered_by=user, updated_by=user)
        year = Season.objects.get(current=True)
        weeks = Week.objects.filter(year=year, gt='POST')
        afc_teams = Team.objects.filter(conference='AFC')
        nfc_teams = Team.objects.filter(conference='NFC')
        print(f'found weeks for post season: {weeks.count()}')
        # games = Game.objects.filter(week__in=weeks)
        # print(f'found games for post season: {games.count()}')
        # for game in Game.objects.filter(week__in=weeks):
        for type in PostPickGame.PSTYPE:
            print(f'create game for {type}')
            seeds = None
            games = None
#TODO: make this logic common function so it can be reused later
            if type == PostPickGame.PSTYPE.AWC45:
                print(f'Type is : {type}')
                # try to find 4 seed AFC team
                seeds = Seed.objects.filter(year=year, seed=4, team__in=afc_teams)
                print(f'Seed is : {seeds[0].seed}')
                week = weeks[0]  # week 18 WC
            elif type == PostPickGame.PSTYPE.AWC36:
                # try to find 3 seed AFC team
                seeds = Seed.objects.filter(year=year, seed=3, team__in=afc_teams)
                week = weeks[0]
            elif type == PostPickGame.PSTYPE.ADIV1:
                # try to find 1 seed AFC team
                seeds = Seed.objects.filter(year=year, seed=1, team__in=afc_teams)
                week = weeks[1] # week 19 DIV
            elif type == PostPickGame.PSTYPE.ADIV2:
                # try to find 2 seed AFC team
                seeds = Seed.objects.filter(year=year, seed=2, team__in=afc_teams)
                week = weeks[1] # week 19 DIV
            elif type == PostPickGame.PSTYPE.NWC45:
                # try to find 4 seed NFC team
                seeds = Seed.objects.filter(year=year, seed=4, team__in=nfc_teams)
                week = weeks[0]  # week 18 WC
            elif type == PostPickGame.PSTYPE.NWC36:
                # try to find 3 seed team
                seeds = Seed.objects.filter(year=year, seed=3, team__in=nfc_teams)
                week = weeks[0]
            elif type == PostPickGame.PSTYPE.NDIV1:
                # try to find 1 seed team
                seeds = Seed.objects.filter(year=year, seed=1, team__in=nfc_teams)
                week = weeks[1] # week 19 DIV
            elif type == PostPickGame.PSTYPE.NDIV2:
                # try to find 2 seed team
                seeds = Seed.objects.filter(year=year, seed=2, team__in=nfc_teams)
                week = weeks[1] # week 19 DIV

            if seeds != None and seeds.count() > 0:
                games = Game.objects.filter(week=week, home_team=seeds[0].team)
            else:
                if type == PostPickGame.PSTYPE.ACONF:
                    week = weeks[2]  # week 20 Conference Championship
                    # games = Game.objects.filter(week=week, home_team__in=afc_teams)
#TODO: switch back to getting the game
                    games = None
                elif type == PostPickGame.PSTYPE.NCONF:
                    week = weeks[2]  # week 20 Conference Championship
                    # games = Game.objects.filter(week=week, home_team__in=nfc_teams)
# TODO: switch back to getting the game
                    games = None
                elif type == PostPickGame.PSTYPE.SB:
                    week = weeks[3]  # week 22 Super Bowl!
                    # games = Game.objects.filter(week=week)
# TODO: switch back to getting the game
                    games = None

            if games != None and games.count() > 0:
                game = games[0]
            else:
                game = None
            # try:
            #     seed = Seed.objects.get(year=year, team=game.home_team)
            # except:
            #     seed = None
            # print(f'found seed for game: {game.gsis}')
            # if seed is not None:
            #     if game.home_team.conference == 'AFC':
            #         if game.wk_no == 18 and seed.seed == 4:
            #             ps_type = 'AWC45'
            #         elif game.wk_no == 18 and seed.seed == 3:
            #             ps_type = 'AWC36'
            #         elif game.wk_no == 19 and seed.seed == 1:
            #             ps_type = 'ADIV1'
            #         elif game.wk_no == 19 and seed.seed == 2:
            #             ps_type = 'ADIV2'
            #         elif game.wk_no == 20:
            #             ps_type = 'ACONF'
            #         elif game.wk_no == 22:
            #             ps_type = 'SB'
            #         else: ps_type = None
            #     elif game.home_team.conference == 'NFC':
            #         if game.wk_no == 18 and seed.seed == 4:
            #             ps_type = 'NWC45'
            #         elif game.wk_no == 18 and seed.seed == 3:
            #             ps_type = 'NWC36'
            #         elif game.wk_no == 19 and seed.seed == 1:
            #             ps_type = 'NDIV1'
            #         elif game.wk_no == 19 and seed.seed == 2:
            #             ps_type = 'NDIV2'
            #         elif game.wk_no == 20:
            #             ps_type = 'NCONF'
            #         elif game.wk_no == 22:
            #             ps_type = 'SB'
            #         else:
            #             ps_type = None
            #     else:
            #         ps_type = None
            # else:
            #     ps_type = None
            #
            # game_pick = PostPickGame.objects.create(post_pick_head=pick, ps_type=ps_type, game=game, entered_by=user,updated_by=user)
            game_pick = PostPickGame.objects.create(post_pick_head=pick, ps_type=type, game=game, entered_by=user,updated_by=user)
            game_pick.save()
            print(f'game saved for post season: {game_pick.ps_type}')
        pick.save()
        return pick


class PostPick(models.Model):
    class Meta:
        verbose_name = 'post season pick'
        verbose_name_plural = 'post season picks'
        indexes = [models.Index(fields=['user'])]
        ordering = ['user']
        constraints = [models.UniqueConstraint(fields=['user'], name='ps_pick_user')]

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL, default=3)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='post_picks',default=1)
    points = models.PositiveSmallIntegerField(default=0)
    pick_score = models.PositiveSmallIntegerField(default=0)
    saved = models.BooleanField(default=False)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='post_pick_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='post_pick_updated')
    # round_id = models.PositiveSmallIntegerField()

    objects = PostPickManager()

    def calc_score(self):
        sum_score = 0
        for pg in self.pickgame_set.all():
            sum_score += pg.pick_score()

        return sum_score


class PostPickGame(models.Model):
    class Meta:
        verbose_name = 'post seasin pick game'
        verbose_name_plural = 'post seasonpick games'

    class PSTYPE(Enum):
        AWC45 = ('AWC45', 'AFC Wild Card 45')
        NWC45 = ('NWC45', 'NFC Wild Card 45')
        AWC36 = ('AWC36', 'AFC Wild Card 36')
        NWC36 = ('NWC36', 'NFC Wild Card 36')
        ADIV1 = ('ADIV1', 'AFC Divisional 1')
        ADIV2 = ('ADIV2', 'AFC Divisional 2')
        NDIV1 = ('NDIV1', 'NFC Divisional 1')
        NDIV2 = ('NDIV2', 'NFC Divisional 2')
        ACONF = ('ACONF', 'AFC Conference Champ')
        NCONF = ('NCONF', 'AFC Conference Champ')
        SB    = ('SB', 'Super Bowl')

        @classmethod
        def get_value(cls,member):
            return cls[member].value[0]


    post_pick_head = models.ForeignKey(PostPick,on_delete=models.CASCADE, related_name='post_games')
    ps_type = models.CharField(max_length=5,choices=[x.value for x in PSTYPE],default=PSTYPE.get_value('AWC45'))
    game = models.ForeignKey(Game,null=True,blank=True,on_delete=models.SET_NULL,related_name='post_pick_game')
    team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='post_pick_team')  #team must be one of 2 teams in the game
    status = models.CharField(max_length=1, null=True)  # W = won, w= Pending win, L = Lost, l= pending loss, T= Tie, t=pending tie
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='post_pick_game_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='_post_pick_game_updated')

    # return 1 if user won the game, 0 if lost or tied
    def pick_score(self):
        if self.game.win_team() == self.team:
            return 1
        else:
            return 0

    def h_team(self):
        if self.game == None:
            hteam = "TBD"
        else:
            hteam = self.game.home_team.short_name
        return hteam

    def v_team(self):
        if self.game == None:
            vteam = "TBD"
        else:
            vteam = self.game.visitor_team.short_name
        return vteam


class PostPoint(models.Model):
    class Meta:
        verbose_name = 'point'
        verbose_name_plural = 'points'
        indexes = [models.Index(fields=['gt'])]
        ordering = ['gt']
        constraints = [models.UniqueConstraint(fields=['gt'], name='gt_pts')]

    gt = models.CharField(max_length=3,null=True) #game type;  REG = Regular Season(1-17); WC = Wild Card(18); DIV = Divisional(19); CON = Conference(20); SB = Super Bowl (22)
    points = models.PositiveSmallIntegerField()


# class Game(models.Model):  (from Pigskinners script)
#     Year_id = models.PositiveSmallIntegerField()
#     wk = models.ForeignKey(Week,null=True,blank=True,on_delete=models.SET_NULL,related_name='game_wk')
#     game_number = models.PositiveSmallIntegerField()
#     game_date = models.DateField()
#     home_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='home_team')
#     visitor_team = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='visitor_team')
#     points_game = models.BooleanField(default=False)
#     tv_network = models.CharField(max_length=10)


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
