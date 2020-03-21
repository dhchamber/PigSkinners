from django.db import models
from django.db.models import Max, Min, Case, When, Sum, Q, IntegerField
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
import pytz
from datetime import datetime, timedelta
from django.utils import timezone
from enum import Enum


# from django.urls import reverse


class TimeStampMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# must be defined before Profile because it is referenced in favorite team
class Team(models.Model):
    class Meta:
        verbose_name = 'team'
        verbose_name_plural = 'teams'
        indexes = [models.Index(fields=['team_abrev', 'short_name'])]
        # ordering = ['team_name']  # removed so union would work

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

    # def __eq__(self, other):
    #     return self.team_name == other.team_name
    #
    # def __lt__(self, other):
    #     return self.team_name < other.team_name

    def cy_seed(self):
        seed = Seed.objects.get(team=self, year=Season.objects.get(current=True))
        return seed.seed


class Profile(models.Model):
    # additional user data
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    entry_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    ball_pool = models.BooleanField(default=False)
    king_hill_eligable = models.BooleanField(default=False)
    # user updateable options
    intro_sound = models.BooleanField(default=False)
    show_graphics = models.BooleanField(default=False)
    show_video = models.BooleanField(default=False)
    favorite_team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='favorite_team')


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
        indexes = [models.Index(fields=['year', 'current'])]
        ordering = ['year']

    year = models.PositiveSmallIntegerField(null=False, default=2020)
    current = models.BooleanField(null=False, default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    def __str__(self):
        return str(self.year)

    def curr_week(self):
        # end_dt is start of last game of the week, so add 5 hours to be sure game is over
        # end_dt and Now are both UTC so they can be compared
        for week in self.weeks.all():
            if week.end_dt() + timedelta(hours=5) > make_aware(datetime.utcnow(), pytz.utc):
                break

        print(f'week: {week}  week.end_dt {week.end_dt()} Now: {datetime.utcnow()}')
        return week

    def season_scores(self):
        # determine winner or winners for the week
        # update pick scores for each pick for each week for the season

        half1 = Week.objects.filter(year=self, gt='REG', week_no__lt=10)
        half2 = Week.objects.filter(year=self, gt='REG', week_no__gt=9)
        full = Week.objects.filter(year=self, gt='REG')

        # TODO: find way to avoid this every time.  it is slow
        # it is removed and is working so this may not be needed
        # add score fields to model and update
        # for week in self.weeks.all():
        #     for pick in week.pick_wk.all():
        #         pick.pick_score = pick.pickgame_set.all().aggregate(score=Sum(Case(When(status='W', then=1), default=0, output_field=IntegerField(), )))['score']
        #         pick.save()
        #         print(f'calc pick score for week: {week.week_no} user: {pick.user.id} {pick.user.first_name} {pick.user.last_name} score: {pick.pick_score}')

        user_scores = User.objects.all().annotate(half1=Sum('picks__pick_score', filter=Q(picks__wk__in=half1))) \
            .annotate(half2=Sum('picks__pick_score', filter=Q(picks__wk__in=half2))) \
            .annotate(all=Sum('picks__pick_score', filter=Q(picks__wk__in=full)))
        return user_scores

    def season_winner(self):
        # determine winner or winners for the 1st half, 2nd half and overall

        # update pick scores for all picks for all the weeks of the regular season
        winners = {}
        year = Season.objects.get(current=True)
        weeks = Week.objects.filter(year=year, gt='REG')
        for pick in Pick.objects.filter(wk__in=weeks):
            pick.pick_score = pick.pickgame_set.all().aggregate(
                score=Sum(Case(When(status='W', then=1), default=0, output_field=IntegerField(), )))['score']

        # get max scores for the Season
        users = self.season_scores()
        half1_max = users.aggregate(max_score=Max('half1', default=0, output_field=IntegerField(), ))['max_score']
        half2_max = users.aggregate(max_score=Max('half2', default=0, output_field=IntegerField(), ))['max_score']
        all_max = users.aggregate(max_score=Max('all', default=0, output_field=IntegerField(), ))['max_score']
        print(f'1st half max: {half1_max}  2nd half max: {half2_max} overall max: {all_max}')

        # get 1st and 2nd half and overall winner(s)
        winners['half1'] = users.filter(half1=half1_max)
        winners['half2'] = users.filter(half2=half2_max)
        winners['all'] = users.filter(all=all_max)
        return winners

    # def get_absolute_url(self):
    #     return reverse('season_detail',args=[str(self.id)])

    # def start_dt(self):
    #     return self.game_wk.aggregate(mind=Min('date_time'))['mind']
    #
    # def end_dt(self):
    #     return self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']


# TODO: start and end are not needed or can be compputed from Game model on the fly as min max of date/time
# TODO: as can forecast date closed, but maybe better to calc and store in table
class Week(models.Model):
    class Meta:
        verbose_name = 'week'
        verbose_name_plural = 'weeks'
        indexes = [models.Index(fields=['year', 'week_no', 'gt', 'closed'])]
        ordering = ['year', 'week_no']

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL, related_name='weeks')
    # TODO: need a way to sort correctly be week and week type, add new model for gt with key 1,2,3 ??
    week_no = models.PositiveSmallIntegerField(
        null=False)  # ? week of the season 1-17, 18-21  must be equal to id for foreign key
    # game type REG = Reg Season(1-17); WC = (18); DIV = (19); CON = (20); SB = (22)
    gt = models.CharField(max_length=3)
    closed = models.BooleanField(default=False)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, default=1)
    date_closed = models.DateTimeField(blank=True, null=True)
    actual_date_closed = models.DateTimeField(blank=True, null=True)
    graphics_folder = models.CharField(max_length=100, null=True, blank=True)
    standings_report_ran = models.BooleanField(default=False)
    weekly_standings_html = models.TextField(blank=True)
    mobile_standings_report_ran = models.BooleanField(default=False)
    mobile_weekly_standings_html = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    forecast_date_closed = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.week_no) + '/' + str(self.gt)

    def create_picks(self):
        for user in User.objects.all():
            if user.is_active:
                try:
                    pick = Pick.objects.get(user=user, wk=self)
                except:
                    pick = Pick.objects.create_pick(user=user, week=self)

    def start_dt(self):
        return self.game_wk.aggregate(mind=Min('date_time'))['mind']

    def end_dt(self):
        return self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']

    def forecast_dt_closed(self):
        if self.start_dt():
            return self.start_dt() - timedelta(hours=2)

    def postseason_week(self):
        timezone.activate(pytz.timezone('America/Denver'))
        min_date = self.game_wk.aggregate(mind=Min('date_time'))['mind']
        max_date = self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']
        print(f'Week: {self.week_no} / min date: {min_date}, max date: {max_date}')
        print(f'Week: {self.week_no} / min date day: {min_date.strftime("%d") }, max date day: {max_date.strftime("%d") }')
        if min_date.strftime("%d") == max_date.strftime("%d"):
            date_str = min_date.strftime("%b. %d")
        else:
            date_str = min_date.strftime("%b. %d") + '-' + max_date.strftime("%d")
        return date_str

    def week_winner(self):
        # determine winner or winners for the week
        # update pick scores for all picks for the week
        for pick in self.pick_wk.all():
            pick.pick_score = pick.pickgame_set.all().aggregate(
                score=Sum(Case(When(status='W', then=1), default=0, output_field=IntegerField(), )))['score']

        #  only return winners if the week is closed
        # should this be only if all games are complete?  af
        if self.closed:
            # get max score for the week
            max_score = \
                self.pick_wk.all().aggregate(max_score=Max('pick_score', default=0, output_field=IntegerField(), ))[
                    'max_score']
            picks = Pick.objects.filter(wk=self).annotate(
                score=Sum(Case(When(pickgame__status='W', then=1), default=0, output_field=IntegerField(), )))
            winners = picks.filter(score=max_score)

            if winners.count() > 1:
                min_delta = 100
                win_ids = []
                for pick in winners:
                    min_delta = min(min_delta, pick.points_delta())
                for pick in winners:
                    if pick.points_delta() == min_delta:
                        win_ids.append(pick.id)
                winners = winners.filter(id__in=win_ids)
        else:
            winners = Pick.objects.none()
        return winners

    # number of players remaining in KOTH this week
    def koth_remaining(self):
        remaining = 0
        for pick in self.pick_wk.all():
            if pick.koth_eligible():
                remaining += 1
                print(f'koth eligible:', pick.user.first_name, remaining)

        return remaining

    # number of players eliminated from KOTH this week
    def koth_eliminated(self):
        eliminated = 0
        for pick in self.pick_wk.all():
            if pick.koth_game is not None and pick.koth_team == pick.koth_game.game_loser():
                eliminated += 1
        return eliminated

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

    # for dev and testing purposes to set game status for the week.  Normally would be set when the game is loaded
    def update_score(self):
        for game in self.game_wk.all():
            game.update_score()

    # def date_range(self):
    #     min_date = self.game_wk.aggregate(mind=Min('date_time'))['mind']
    #     max_date = self.game_wk.all().aggregate(maxd=Max('date_time'))['maxd']
    #     print(f'{min_date.strftime("%m-%d-%Y")} to {max_date.strftime("%m-%d-%Y")}')
    #     return min_date.strftime('%m-%d-%Y') + ' to ' + max_date.strftime('%m-%d-%Y')


class Game(TimeStampMixin):
    class Meta:
        verbose_name = 'game'
        verbose_name_plural = 'games'
        indexes = [models.Index(fields=['week', 'year', 'eid', 'gsis'])]
        ordering = ['eid', 'gsis']

    # Fields
    # from xml file gms header for each week
    gd = models.PositiveSmallIntegerField(null=True)  # ? always zero?
    week = models.ForeignKey(Week, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name='game_wk')  # key to ID in week table based on year and wk_no
    wk_no = models.PositiveSmallIntegerField(null=True)  # week of the NFL season 1-17, 18-20, 22
    year = models.PositiveSmallIntegerField(null=True)  # season year
    t = models.CharField(max_length=10, null=True)  # ? P = Post Season, R = Regular Season ?
    bf = models.CharField(max_length=10, null=True)  # ? 1?   from liveupdate postseason
    bph = models.CharField(max_length=10, null=True)  # ? 0? 172?  from liveupdate
    # from g record for each game
    eid = models.CharField(max_length=10)  # date of game and count number
    gsis = models.CharField(max_length=10)  # ID of game game key
    day = models.CharField(max_length=3)  # day of the week of game
    time = models.CharField(max_length=5, null=True)  # time of game in hh:mm format Eastern Time
    date_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=3)  # statue of game F= Finished; FO = Finished Overtime; P = Pending?;
    k = models.CharField(max_length=1, null=True)  # ???
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home')
    home = models.CharField(max_length=3)  # home team abreviation            HOU
    home_nickname = models.CharField(max_length=20, null=True)  # home team nickname     texans
    home_teamname = models.CharField(max_length=20, null=True)  # home team name         Houston Texans
    home_score = models.PositiveSmallIntegerField(null=True)  # home team score
    visitor_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='visitor')
    visitor = models.CharField(max_length=3)  # visitor team abreviation
    visitor_nickname = models.CharField(max_length=20, null=True)  # visitor team nickname
    visitor_teamname = models.CharField(max_length=20, null=True)  # visitor team nickname
    visitor_score = models.PositiveSmallIntegerField(null=True)  # visitor team score
    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='wins')
    p = models.CharField(max_length=1, null=True)  # possession
    network = models.CharField(max_length=20, null=True)
    red_zone = models.CharField(max_length=1, null=True)  # ???
    ga = models.CharField(max_length=2, null=True)  # ???
    # game type?  REG = Regular Season(1-17); WC = Wild Card(18); DIV = Div(19); CON = Conf(20); SB =  (22)
    gt = models.CharField(max_length=3, null=True)
    points_game = models.BooleanField(default=False)

    def __str__(self):
        return self.gsis

    def points_score(self):
        return self.home_score + self.visitor_score

    def get_date(self):
        # the time of the game from the game feed is in Eastern time, convert to Mountain
        year = int(self.eid[:4])
        mo = int(self.eid[4:6])
        day = int(self.eid[6:8])
        hour, min = self.time.split(':')
        # TODO: there is a problem with some times in week 13  need to handle this
        if int(hour) < 12:
            est_date = make_aware(datetime(year, mo, day, int(hour) + 12, int(min)), pytz.timezone('America/New_York'))
        else:
            est_date = make_aware(datetime(year, mo, day, int(hour), int(min)), pytz.timezone('America/New_York'))
        mst_date = est_date.astimezone(pytz.timezone('America/Denver'))  # conver date to MST
        return mst_date

    # TODO: rename to indicate currently winning team for prospective standings
    def win_team(self):
        if self.home_score > self.visitor_score:
            return self.home_team
        elif self.home_score < self.visitor_score:
            return self.visitor_team
        else:
            pass

    # changed to just show final games for KOTH standings
    def lose_team(self):
        if self.status == 'F' or self.status == 'FO':
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

    # should these 2 be combined with a parameter?
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

    def game_loser(self):
        if self.status == 'F' or self.status == 'FO':
            if self.home_score < self.visitor_score:
                return self.home_team
            elif self.home_score > self.visitor_score:
                return self.visitor_team
            elif self.home_score == self.visitor_score:
                return 'Tie'
            else:
                return 'Error'

    def update_score(self):
        # get all the pick games that have a pick for this game and update the status as won or lost
        pgames = self.pick_game.all()
        for pg in pgames:
            if pg.team is not None:
                if self.status == 'P':
                    if pg.team == self.winner:
                        pg.status = 'w'
                    elif self.home_score == self.visitor_score:
                        pg.status = 't'
                    else:
                        pg.status = 'l'
                else:
                    if pg.team == self.winner:
                        pg.status = 'W'
                    elif self.home_score == self.visitor_score:
                        pg.status = 'T'
                    else:
                        pg.status = 'L'
                pg.save()
                pg.pick_head.calc_score()
                print(f'update score on pick: {pg.pick_head.id} with score: {pg.pick_head.calc_score()}')

    def set_winner(self):
        if self.status[:1] == 'F':
            if self.home_score > self.visitor_score:
                self.winner = self.home_team
            elif self.home_score < self.visitor_score:
                self.winner = self.visitor_team
            else:
                self.winner = None
        self.save()


#  Table for PostSeason seeds
class Seed(models.Model):
    class Meta:
        verbose_name = 'seed'
        verbose_name_plural = 'seeds'
        indexes = [models.Index(fields=['year', 'team'])]
        ordering = ['year', 'team', 'seed']
        constraints = [models.UniqueConstraint(fields=['year', 'team'], name='year_team')]

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='seeds')
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='gm_seeds')
    seed = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return str(self.seed)


#  Table for PostSeason games
class PostSeason(models.Model):
    class Meta:
        verbose_name = 'post season game'
        verbose_name_plural = 'post season games'
        indexes = [models.Index(fields=['year'])]
        ordering = ['year']
        constraints = [models.UniqueConstraint(fields=['year'], name='ps_year')]
#
#     class PSTYPE(Enum):
#         AWC45 = ('AWC45', 'AFC Wild Card 45')
#         NWC45 = ('NWC45', 'NFC Wild Card 45')
#         AWC36 = ('AWC36', 'AFC Wild Card 36')
#         NWC36 = ('NWC36', 'NFC Wild Card 36')
#         ADIV1 = ('ADIV1', 'AFC Divisional 1')
#         ADIV2 = ('ADIV2', 'AFC Divisional 2')
#         NDIV1 = ('NDIV1', 'NFC Divisional 1')
#         NDIV2 = ('NDIV2', 'NFC Divisional 2')
#         ACONF = ('ACONF', 'AFC Conference Champ')
#         NCONF = ('NCONF', 'AFC Conference Champ')
#         SB = ('SB', 'Super Bowl')
#
#         @classmethod
#         def get_value(cls, member):
#             return cls[member].value[0]
#
    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL)
    AWC45 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='AWC45_game')
    NWC45 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='NWC45_game')
    AWC36 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='AWC36_game')
    NWC36 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='NWC36_game')
    ADIV1 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='ADIV1_game')
    ADIV2 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='ADIV2_game')
    NDIV1 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='NDIV1_game')
    NDIV2 = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='NDIV2_game')
    ACONF = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='ACONF_game')
    NCONF = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='NCONF_game')
    SB = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='SB_game')

        #     ps_type = models.CharField(max_length=5, choices=[x.value for x in PSTYPE], default=PSTYPE.get_value('AWC45'))
#     game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='post_game')
#
#     def __str__(self):
#         return str(self.PSTYPE)


class PickManager(models.Manager):
    def create_pick(self, user, week):
        pick = self.create(user=user, wk=week, points=0, entered_by=user, updated_by=user)
        for game in Game.objects.filter(week=week):
            game_picks = PickGame.objects.create(pick_head=pick, game=game, entered_by=user, updated_by=user)
            game_picks.save()
        pick.save()
        return pick

    def save_pick(self):
        if Pick.validate_pick(self):
            self.saved = True
            self.save()


class Pick(models.Model):
    class Meta:
        verbose_name = 'pick'
        verbose_name_plural = 'picks'
        indexes = [models.Index(fields=['user', 'wk'])]
        ordering = ['user', 'wk']
        constraints = [models.UniqueConstraint(fields=['user', 'wk'], name='pick_uweser_wk')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='picks', default=1)
    wk = models.ForeignKey(Week, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_wk')
    points = models.PositiveSmallIntegerField()
    koth_game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='koth_game')
    koth_team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='koth_team')
    pick_score = models.PositiveSmallIntegerField(default=0)
    saved = models.BooleanField(default=False)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_updated')

    objects = PickManager()

    # TODO: retrun message with what failed
    def validate_pick(self):
        validate = True
        if self.points is None or self.points == 0:
            validate = False
        elif self.koth_game is None:
            validate = False
        elif self.koth_team is None:
            validate = False

        for pg in self.pickgame_set.all():
            if pg.game is None:
                validate = False
            elif pg.team is None:
                validate = False
        return validate

    def pick_year(self):
        return self.wk.year

    # def koth_eligible(self):
    #     year = Season.objects.get(current=True)
    #     weeks = Week.objects.filter(year=year, gt='REG', closed=True)
    #     picks = Pick.objects.filter(user=self.user, wk__in=weeks)
    #     eligible = True
    #     for pick in picks:
    #         if pick.koth_game:  # remove this.  if week is closed and no pick then eliminated
    #             if pick.koth_team == pick.koth_game.game_loser():
    #                 eligible = False
    #                 break
    #     return eligible

    # return 1 if user won KOTH game, 0 if lost or tied
    def koth_score(self):
        if self.koth_team is not None and self.koth_game is not None and self.koth_game.game_winner() == self.koth_team:
            return 1
        else:
            return 0

    # is the player still eligible for KOTH, no missed picks, no losses
    def koth_eligible(self):
        year = Season.objects.get(current=True)
        weeks = Week.objects.filter(year=year, gt='REG', closed=True)
        eligible = True
        for week in weeks:
            try:
                pick = Pick.objects.get(user=self.user, wk=week)
                if pick.koth_game is None or pick.koth_team is None or pick.koth_team == pick.koth_game.game_loser():
                    eligible = False
                    break
            except pick.DoesNotExist:
                eligible = False
                break
        return eligible

    # teams that player still has available for KOTH
    def koth_remaining(self):
        year = Season.objects.get(current=True)
        weeks = Week.objects.filter(year=year, gt='REG', closed=True)
        # used_picks = Pick.objects.filter(user=self.user, wk__in=weeks).values_list('koth_team', flat=True)
        home = Team.objects.filter(Q(home__week=self.wk))
        visitor = Team.objects.filter(Q(visitor__week=self.wk))
        used = Team.objects.filter(Q(koth_team__wk__in=weeks) & Q(koth_team__user=self.user))
        teams = home.union(visitor).difference(used).order_by('team_name')

        return teams

    def calc_score(self):
        sum_score = 0
        for pg in self.pickgame_set.all():
            sum_score += pg.pick_score()
        self.pick_score = sum_score
        self.save()

        return sum_score

    def points_delta(self):
        pts_game = Game.objects.filter(week=self.wk, points_game=True)
        if pts_game.count() > 0:
            pts = pts_game[0].points_score()
            pts_delta = abs(self.points - pts)
        else:
            pts_delta = None
        return pts_delta

    def cap_user(self):
        return self.user.capitalize()


class PickGame(models.Model):
    class Meta:
        verbose_name = 'pick game'
        verbose_name_plural = 'pick games'

    pick_head = models.ForeignKey(Pick, on_delete=models.CASCADE)  # ,related_name='pick_head'
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_game')
    # team must be one of 2 teams in the game
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_team')
    # W = won, w= Pending win, L = Lost, l= pending loss, T= Tie, t=pending tie
    status = models.CharField(max_length=1, null=True)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_game_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_game_updated')

    # return 1 if user won the game, 0 if lost or tied
    def pick_score(self):
        if self.game.game_winner() == self.team:  # change from win_team to game_winner
            return 1
        else:
            return 0


class PostPickManager(models.Manager):
    def create_ps_pick(self, year, user):
        post_pick = self.create(year=year, user=user, entered_by=user, updated_by=user)
        # year = Season.objects.get(current=True)
        # weeks = Week.objects.filter(year=year, gt='POST')
        # print(f'found weeks for post season: {weeks.count()}')
        # games = Game.objects.filter(week__in=weeks)
        # print(f'found games for post season: {games.count()}')
        # for game in Game.objects.filter(week__in=weeks):
        post_pick.set_seed_game(user)
        post_pick.save()
        return post_pick


# TODO: add mixin dates
class PostPick(models.Model):
    class Meta:
        verbose_name = 'post season pick'
        verbose_name_plural = 'post season picks'
        indexes = [models.Index(fields=['year', 'user'])]
        ordering = ['year', 'user']
        constraints = [models.UniqueConstraint(fields=['year', 'user'], name='ps_pick_user')]

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL, default=3)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_picks', default=1)
    points = models.PositiveSmallIntegerField(default=0)
    pick_score = models.PositiveSmallIntegerField(default=0)
    saved = models.BooleanField(default=False)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_pick_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_pick_updated')
    # round_id = models.PositiveSmallIntegerField()

    objects = PostPickManager()

    def calc_score(self):
        sum_score = 0
        for pg in self.post_games.all():
            sum_score += int(pg.pick_score())
        return sum_score

    def points_rem(self):
        # possible point remaining if game is not defined yet, or
        # game is not final and you have a team in the game
        rem = 0
        print(f'rem: {rem}')
        for pg in self.post_games.all():
            if pg.game is None:
                gt = pg.pstype_gt()
                points = PostPoint.objects.get(gt=gt)
                rem += int(points.points)
                print(f'Points {points} for {gt} game not defined yet. rem: {rem}')
            elif pg.game.status == 'P':
                # do you have a team in the game?
                if pg.team == pg.game.home_team or pg.team == pg.game.visitor_team:
                    rem += int(pg.pick_score())
            else:
                rem += 0
        return rem

    def set_seed_game(self, user):
        year = Season.objects.get(current=True)
        weeks = Week.objects.filter(year=year, gt='POST')

        afc_teams = Team.objects.filter(conference='AFC')
        nfc_teams = Team.objects.filter(conference='NFC')

        for type in PostPickGame.PSTYPE:
            print(f'create game for {type}')
            seeds = None
            games = None
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
                week = weeks[1]  # week 19 DIV
            elif type == PostPickGame.PSTYPE.ADIV2:
                # try to find 2 seed AFC team
                seeds = Seed.objects.filter(year=year, seed=2, team__in=afc_teams)
                week = weeks[1]  # week 19 DIV
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
                week = weeks[1]  # week 19 DIV
            elif type == PostPickGame.PSTYPE.NDIV2:
                # try to find 2 seed team
                seeds = Seed.objects.filter(year=year, seed=2, team__in=nfc_teams)
                week = weeks[1]  # week 19 DIV

            if seeds is not None and seeds.count() > 0:
                games = Game.objects.filter(week=week, home_team=seeds[0].team)
            else:
                if type == PostPickGame.PSTYPE.ACONF:
                    week = weeks[2]  # week 20 Conference Championship
                    # games = Game.objects.filter(week=week, home_team__in=afc_teams)
                    # TODO: switch back to getting the game
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

            if games is not None and games.count() > 0:
                game = games[0]
            else:
                game = None
            game_pick = PostPickGame.objects.create(post_pick_head=self, ps_type=type, game=game, entered_by=user,
                                                    updated_by=user)
            game_pick.save()
            print(f'game saved for post season: {game_pick.ps_type}')

# TODO: since the games are fixed in Post Season, should this just be all part of the header table?
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
        SB = ('SB', 'Super Bowl')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    post_pick_head = models.ForeignKey(PostPick, on_delete=models.CASCADE, related_name='post_games')
    ps_type = models.CharField(max_length=5, choices=[x.value for x in PSTYPE], default=PSTYPE.get_value('AWC45'))
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='post_pick_game')
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='post_pick_team')  # team must be one of 2 teams in the game
    status = models.CharField(max_length=1,
                              null=True)  # W = won, w= Pending win, L = Lost, l= pending loss, T= Tie, t=pending tie
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='post_pick_game_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='_post_pick_game_updated')

    # return 1 if user won the game, 0 if lost or tied
    def pick_score(self):
        if self.game is not None and self.game.win_team() == self.team:
            pts = PostPoint.objects.get(gt=self.game.gt)
            return pts.points
        else:
            return 0

    def h_team(self):
        if self.game is None:
            hteam = "TBD"
        else:
            hteam = self.game.home_team.short_name
        return hteam

    def v_team(self):
        if self.game is None:
            vteam = "TBD"
        else:
            vteam = self.game.visitor_team.short_name
        return vteam

    def pstype_gt(self):
        if self.ps_type[8:10] == "WC":
            return 'WC'
        elif self.ps_type[8:11] == "DIV":
            return 'DIV'
        elif self.ps_type[8:] == "CONF":
            return 'CON'
        elif self.ps_type[7:] == "SB":
            return 'SB'
        else:
            return 'X'

class PostPick2Manager(models.Manager):
    def create_ps_pick(self, year, user):
        post_pick = self.create(year=year, user=user, entered_by=user, updated_by=user)
        # post_pick.set_seed_game(user)
        post_pick.save()
        return post_pick

    def save_pick(self):
        # if Pick.validate_pick(self):
        self.saved = True
        self.save()


class PostPick2(models.Model):
    class Meta:
        verbose_name = 'post season pick2'
        verbose_name_plural = 'post season picks2'
        indexes = [models.Index(fields=['year', 'user'])]
        ordering = ['year', 'user']
        constraints = [models.UniqueConstraint(fields=['year', 'user'], name='ps_pick_user2')]

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL, default=3)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_post_picks', default=1)
    points = models.PositiveSmallIntegerField(default=0)
    AWC45 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='AWC45_team')
    NWC45 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='NWC45_team')
    AWC36 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='AWC36_team')
    NWC36 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='NWC36_team')
    AvtDiv1 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='AtDiv1_team')
    NvtDiv1 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='NtDiv1_team')
    AvtDiv2 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='AtDiv2_team')
    NvtDiv2 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='NtDiv2_team')
    ADIV1 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='ADIV1_team')
    ADIV2 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='ADIV2_team')
    NDIV1 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='NDIV1_team')
    NDIV2 = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='NDIV2_team')
    ACONF = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='ACONF_team')
    NCONF = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='NCONF_team')
    SB    = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='SB_team')
    pick_score = models.PositiveSmallIntegerField(default=0)
    saved = models.BooleanField(default=False)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_pick2_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_pick2_updated')

    objects = PostPick2Manager()

    def calc_score(self):
        sum_score = 0
        # for pg in self.post_games.all():
        #     sum_score += int(pg.pick_score())
        return sum_score

    def points_rem(self):
        # possible point remaining if game is not defined yet, or
        # game is not final and you have a team in the game
        rem = 0
        print(f'rem: {rem}')
        # for pg in self.post_games.all():
        #     if pg.game is None:
        #         gt = pg.pstype_gt()
        #         points = PostPoint.objects.get(gt=gt)
        #         rem += int(points.points)
        #         print(f'Points {points} for {gt} game not defined yet. rem: {rem}')
        #     elif pg.game.status == 'P':
        #         # do you have a team in the game?
        #         if pg.team == pg.game.home_team or pg.team == pg.game.visitor_team:
        #             rem += int(pg.pick_score())
        #     else:
        #         rem += 0
        return rem



class PostPoint(models.Model):
    class Meta:
        verbose_name = 'point'
        verbose_name_plural = 'points'
        indexes = [models.Index(fields=['gt'])]
        ordering = ['gt']
        constraints = [models.UniqueConstraint(fields=['gt'], name='gt_pts')]

    gt = models.CharField(max_length=3, null=True)  # game type; WC, DIV, CON, SB
    points = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.points)

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
#   winner_team_id = models.ForeignKey(Team,null=True,blank=True,on_delete=models.SET_NULL,related_name='result_winner')
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
