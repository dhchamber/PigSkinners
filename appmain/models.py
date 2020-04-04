from django.db import models
from django.db.models import Max, Min, Case, When, Sum, Q, IntegerField
from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField
from django.utils.translation import ugettext_lazy as _  # for TimeStampMixin
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware
import pytz
from datetime import datetime, timedelta
from django.utils import timezone
import logging
# from enum import Enum
# from django.urls import reverse

logger = logging.getLogger(__name__)

# List of NFL weeks, 4 PreSeason, 17 Regular Season, and 4 Post Season
nfl_week = [(1, 'PRE'), (2, 'PRE'), (3, 'PRE'), (4, 'PRE'), (1, 'REG'), (2, 'REG'), (3, 'REG'), (4, 'REG'), (5, 'REG'),
            (6, 'REG'), (7, 'REG'), (8, 'REG'), (9, 'REG'), (10, 'REG'), (11, 'REG'), (12, 'REG'), (13, 'REG'),
            (14, 'REG'), (15, 'REG'), (16, 'REG'), (17, 'REG'), (18, 'POST'), (19, 'POST'), (20, 'POST'), (22, 'POST')]


class TimeStampMixin(models.Model):
    # TimeStampedModel
    # https: // github.com / django - extensions / django - extensions / blob / master / django_extensions / db / models.py
    # An abstract base class model that provides self-managed "created" and
    # "modified" fields.

    # created = models.DateTimeField(auto_now_add=True)
    # updated = models.DateTimeField(auto_now=True)

    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    def save(self, **kwargs):
        self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
        super(TimeStampMixin, self).save(**kwargs)

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True


# must be defined before Profile because it is referenced in favorite team
class Team(models.Model):
    class Meta:
        verbose_name = 'team'
        verbose_name_plural = 'teams'
        indexes = [models.Index(fields=['team_abrev', 'short_name'])]
        constraints = [models.UniqueConstraint(fields=['team_abrev'], name='abrev_team')]
        # ordering = ['team_name']  # removed so union would work

    team_name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)
    team_abrev = models.CharField(max_length=3)
    # web_address = models.URLField(max_length=200)
    # logo = models.CharField(max_length=50)
    division = models.CharField(max_length=50, default='NA')
    # logo_file_name = models.CharField(max_length=50)
    win = models.SmallIntegerField(default=0)
    lose = models.SmallIntegerField(default=0)
    tie = models.SmallIntegerField(default=0)
    conference = models.CharField(max_length=50, default='NA')
    city_name = models.CharField(max_length=50, default= 'NA')

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

    def set_season_weeks(self):
        # load week objects for a new year.
        # print(f'Loading weeks for {self} ')
        logger.debug(f'Loading weeks for {self} ')
        for week, gt in nfl_week:
            week, created = Week.objects.get_or_create(year=self, week_no=week, gt=gt)
            week.save()
            # print(f'Week # {week} {gt} loaded ')
            logger.debug(f'Week # {week} {gt} loaded ')

    # def load_games(self):
    #     # yr = season
    #     # game_first = -4 # start at -4 to get PreSeason games
    #     # game_last = 22  # 22 is SB
    #     for week, gt in nfl_week:
    #         load_score('WEEK', self, gt, week)

    def current_week(self):
        # end_dt is start of last game of the week, so add 5 hours to be sure game is over
        # end_dt and Now are both UTC so they can be compared
        for week in self.weeks.all():
            # if week.end_dt() + timedelta(hours=5) > make_aware(datetime.utcnow(), pytz.utc):
            if week.week_no == 5:
                break
        if not self.weeks.all():  # there are no weeks in the Season
            logger.debug(f'There are no weeks in Season {self.year}')
            week = None
        else:
            # print(f'week: {week}  week.end_dt {week.end_dt()} Now: {datetime.utcnow()}')
            logger.debug(f'week: {week}  week.end_dt {week.end_dt()} Now: {datetime.utcnow()}')
        return week

    def season_scores(self):
        # determine winner or winners for the week
        # update pick scores for each pick for each week for the season

        half1 = Week.objects.filter(year=self, gt='REG', week_no__lt=10)
        half2 = Week.objects.filter(year=self, gt='REG', week_no__gt=9)
        full = Week.objects.filter(year=self, gt='REG')

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
        # print(f'1st half max: {half1_max}  2nd half max: {half2_max} overall max: {all_max}')
        logger.debug(f'1st half max: {half1_max}  2nd half max: {half2_max} overall max: {all_max}')

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


class Week(models.Model):
    class Meta:
        verbose_name = 'week'
        verbose_name_plural = 'weeks'
        indexes = [models.Index(fields=['year', 'week_no', 'gt', 'closed'])]
        ordering = ['year', 'id']

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL, related_name='weeks')
    week_no = models.PositiveSmallIntegerField(null=False)  # ? week of the season 1-17, 18-21
    gt = models.CharField(max_length=4)
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
                except Pick.DoesNotExist:
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
        # print(f'Week: {self.week_no} / min date: {min_date}, max date: {max_date}')
        logger.debug(f'Week: {self.week_no} / min date: {min_date}, max date: {max_date}')
        logger.debug(f'Week: {self.week_no}/min_date: {min_date.strftime("%d")}/max_date: {max_date.strftime("%d")}')
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
                # print(f'koth eligible:', pick.user.first_name, remaining)
                logger.debug(f'koth eligible:', pick.user.first_name, remaining)

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

    # TODO: this is the same code as in load nfl games.  consolidate!
    def get_date(self):
        # the time of the game from the game feed is in Eastern time, convert to Mountain
        year = int(self.eid[:4])
        mo = int(self.eid[4:6])
        day = int(self.eid[6:8])
        hour, minute = self.time.split(':')
        # TODO: there is a problem with some times in week 13  need to handle this
        if int(hour) < 12:
            est_date = make_aware(datetime(year, mo, day, int(hour) + 12, int(minute)),
                                  pytz.timezone('America/New_York'))
        else:
            est_date = make_aware(datetime(year, mo, day, int(hour), int(minute)), pytz.timezone('America/New_York'))
        mst_date = est_date.astimezone(pytz.timezone('America/Denver'))  # conver date to MST
        return mst_date

    def pros_win_team(self):
        if self.home_score > self.visitor_score:
            return self.home_team
        elif self.home_score < self.visitor_score:
            return self.visitor_team
        else:
            pass

    # changed to just show final games for KOTH standings
    def pros_lose_team(self):
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
                # print(f'update score on pick: {pg.pick_head.id} with score: {pg.pick_head.calc_score()}')
                logger.debug(f'update score on pick: {pg.pick_head.id} with score: {pg.pick_head.calc_score()}')

        pgames = self.pick_rev_game.all()
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
                pg.pickrev_head.calc_score()
                # print(f'update score on pick: {pg.pick_head.id} with score: {pg.pick_head.calc_score()}')
                logger.debug(f'update score on pick revs: {pg.pickrev_head.id} with score: {pg.pickrev_head.calc_score()}')


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

    def get_losers(self):
        losers = []
        if self.AWC45 is not None and self.AWC45.status[:1] == 'F':
            losers.append(self.AWC45.game_loser())

        if self.NWC45 is not None and self.NWC45.status[:1] == 'F':
            losers.append(self.NWC45.game_loser())

        if self.AWC36 is not None and self.AWC36.status[:1] == 'F':
            losers.append(self.AWC36.game_loser())

        if self.NWC36 is not None and self.NWC36.status[:1] == 'F':
            losers.append(self.NWC36.game_loser())

        if self.ADIV1 is not None and self.ADIV1.status[:1] == 'F':
            losers.append(self.ADIV1.game_loser())

        if self.ADIV2 is not None and self.ADIV2.status[:1] == 'F':
            losers.append(self.ADIV2.game_loser())

        if self.NDIV1 is not None and self.NDIV1.status[:1] == 'F':
            losers.append(self.NDIV1.game_loser())

        if self.NDIV2 is not None and self.NDIV2.status[:1] == 'F':
            losers.append(self.NDIV2.game_loser())

        if self.ACONF is not None and self.ACONF.status[:1] == 'F':
            losers.append(self.ACONF.game_loser())

        if self.NCONF is not None and self.NCONF.status[:1] == 'F':
            losers.append(self.NCONF.game_loser())

        if self.SB is not None and self.SB.status[:1] == 'F':
            losers.append(self.SB.game_loser())

        return losers

    def set_games(self):
        year = Season.objects.get(current=True)
        if self.AWC45 is None:
            seed = Seed.objects.filter(year=year, seed=4,
                                       team__in=(team for team in Team.objects.filter(conference='AFC')))
            week = Week.objects.get(year=year, week_no=18, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.AWC45 = game[0]

        if self.AWC36 is None:
            seed = Seed.objects.filter(year=year, seed=3,
                                       team__in=(team for team in Team.objects.filter(conference='AFC')))
            week = Week.objects.get(year=year, week_no=18, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.AWC36 = game[0]

        if self.NWC45 is None:
            seed = Seed.objects.filter(year=year, seed=4,
                                       team__in=(team for team in Team.objects.filter(conference='NFC')))
            week = Week.objects.get(year=year, week_no=18, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.AWC45 = game[0]

        if self.NWC36 is None:
            seed = Seed.objects.filter(year=year, seed=3,
                                       team__in=(team for team in Team.objects.filter(conference='NFC')))
            week = Week.objects.get(year=year, week_no=18, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.NWC36 = game[0]

        if self.ADIV1 is None:
            seed = Seed.objects.filter(year=year, seed=1,
                                       team__in=(team for team in Team.objects.filter(conference='AFC')))
            week = Week.objects.get(year=year, week_no=19, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.ADIV1 = game[0]

        if self.ADIV2 is None:
            seed = Seed.objects.filter(year=year, seed=2,
                                       team__in=(team for team in Team.objects.filter(conference='AFC')))
            week = Week.objects.get(year=year, week_no=19, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.ADIV2 = game[0]

        if self.NDIV1 is None:
            seed = Seed.objects.filter(year=year, seed=1,
                                       team__in=(team for team in Team.objects.filter(conference='NFC')))
            week = Week.objects.get(year=year, week_no=19, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.NDIV1 = game[0]

        if self.NDIV2 is None:
            seed = Seed.objects.filter(year=year, seed=2,
                                       team__in=(team for team in Team.objects.filter(conference='NFC')))
            week = Week.objects.get(year=year, week_no=19, gt="POST")
            game = Game.objects.filter(week=week, home_team=seed[0].team)
            if game.count() > 0:
                self.ADIV2 = game[0]

        if self.ACONF is None:
            week = Week.objects.get(year=year, week_no=20, gt="POST")
            game = Game.objects.filter(week=week,
                                       home_team__in=(team for team in Team.objects.filter(conference='AFC')))
            if game.count() > 0:
                self.ACONF = game[0]

        if self.NCONF is None:
            week = Week.objects.get(year=year, week_no=20, gt="POST")
            game = Game.objects.filter(week=week,
                                       home_team__in=(team for team in Team.objects.filter(conference='NFC')))
            if game.count() > 0:
                self.NCONF = game[0]

        if self.SB is None:
            week = Week.objects.get(year=year, week_no=22, gt="POST")
            game = Game.objects.filter(week=week)
            if game.count() > 0:
                self.SB = game[0]

        self.save()


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


class Pick(TimeStampMixin):
    class Meta:
        verbose_name = 'pick'
        verbose_name_plural = 'picks'
        indexes = [models.Index(fields=['user', 'wk'])]
        ordering = ['user', 'wk']
        constraints = [models.UniqueConstraint(fields=['user', 'wk'], name='pick_user_wk')]

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
            except Pick.DoesNotExist:
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


class PickGame(TimeStampMixin):
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


class PickRevisionManager(models.Manager):
    def create_rev(self, pick):
        print(f'In Create Rev')
        pick_revs = PickRevision.objects.filter(user=pick.user, wk=pick.wk)
        print(f'Got Revs: {pick_revs.count()}')
        if pick_revs:
            new_rev = pick_revs.aggregate(max_rev=Max('revision', default=0, output_field=IntegerField(), ))['max_rev'] + 1
        else:
            new_rev = 1
        pick_rev = self.create(revision=new_rev, user=pick.user, wk=pick.wk, points=pick.points, koth_game=pick.koth_game, koth_team=pick.koth_team, pick_score=pick.pick_score, saved=pick.saved, entered_by=pick.entered_by, updated_by=pick.updated_by)
        for pick_game in pick.pickgame_set.all():
            rev_game = PickRevGame.objects.create(pickrev_head=pick_rev, game=pick_game.game, team=pick_game.team, status=pick_game.status, entered_by=pick_game.entered_by, updated_by=pick_game.updated_by)
            rev_game.save()
        pick.save()
        return pick


class PickRevision(models.Model):
    class Meta:
        verbose_name = 'pick revision'
        verbose_name_plural = 'pick revisions'
        indexes = [models.Index(fields=['revision', 'user', 'wk'])]
        ordering = ['user', 'wk']
        constraints = [models.UniqueConstraint(fields=['revision', 'user', 'wk'], name='pickrev_user_wk')]

    revision = models.PositiveSmallIntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_revs', default=1)
    wk = models.ForeignKey(Week, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_rev_wk')
    points = models.PositiveSmallIntegerField()
    koth_game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_rev_koth_game')
    koth_team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_rev_koth_team')
    pick_score = models.PositiveSmallIntegerField(default=0)
    saved = models.BooleanField(default=False)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_rev_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_rev_updated')

    objects = PickRevisionManager()

    def calc_score(self):
        sum_score = 0
        for pg in self.pickrevgame_set.all():
            sum_score += pg.pick_score()
        self.pick_score = sum_score
        self.save()

        return sum_score

class PickRevGame(models.Model):
    class Meta:
        verbose_name = 'pick game'
        verbose_name_plural = 'pick games'

    pickrev_head = models.ForeignKey(PickRevision, on_delete=models.CASCADE)  # ,related_name='pick_head'
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_rev_game')
    # team must be one of 2 teams in the game
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='pick_rev_team')
    # W = won, w= Pending win, L = Lost, l= pending loss, T= Tie, t=pending tie
    status = models.CharField(max_length=1, null=True)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_rev_game_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pick_rev_game_updated')

    def pick_score(self):
        if self.game.game_winner() == self.team:  # change from win_team to game_winner
            return 1
        else:
            return 0

class PostPickManager(models.Manager):
    def create_ps_pick(self, user, year):
        post_pick = self.create(year=year, user=user, entered_by=user, updated_by=user)
        # post_pick.set_seed_game(user)
        post_pick.save()
        return post_pick

    def save_pick(self):
        # if Pick.validate_pick(self):
        self.saved = True
        self.save()


class PostPick(models.Model):
    class Meta:
        verbose_name = 'post season pick2'
        verbose_name_plural = 'post season picks2'
        indexes = [models.Index(fields=['year', 'user'])]
        ordering = ['year', 'user']
        constraints = [models.UniqueConstraint(fields=['year', 'user'], name='ps_pick_user2')]

    year = models.ForeignKey(Season, null=True, blank=True, on_delete=models.SET_NULL, default=3)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_post_picks',
                             default=1)
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
    SB = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='SB_team')
    pick_score = models.PositiveSmallIntegerField(default=0)
    saved = models.BooleanField(default=False)
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='post_pick2_entered')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='post_pick2_updated')

    objects = PostPickManager()

    def calc_score(self):
        ps_games = PostSeason.objects.get(year=Season.objects.get(current=True))
        points = PostPoint.objects.all()
        score = 0
        if self.AWC45 is not None and ps_games.AWC45 is not None:
            if self.AWC45 == ps_games.AWC45.game_winner():
                score += points[3].points  # add WC points

        if self.AWC36 is not None and ps_games.AWC36 is not None:
            if self.AWC36 == ps_games.AWC36.game_winner():
                score += points[3].points  # add WC points

        if self.NWC45 is not None and ps_games.NWC45 is not None:
            if self.NWC45 == ps_games.NWC45.game_winner():
                score += points[3].points  # add WC points

        if self.NWC36 is not None and ps_games.NWC36 is not None:
            if self.NWC36 == ps_games.NWC36.game_winner():
                score += points[3].points  # add WC points

        if self.ADIV1 is not None and ps_games.ADIV1 is not None:
            if self.ADIV1 == ps_games.ADIV1.game_winner():
                score += points[1].points  # add DIV points

        if self.ADIV2 is not None and ps_games.ADIV2 is not None:
            if self.ADIV2 == ps_games.ADIV2.game_winner():
                score += points[1].points  # add DIV points

        if self.NDIV1 is not None and ps_games.NDIV1 is not None:
            if self.NDIV1 == ps_games.NDIV1.game_winner():
                score += points[1].points  # add DIV points

        if self.NDIV2 is not None and ps_games.NDIV2 is not None:
            if self.NDIV2 == ps_games.NDIV2.game_winner():
                score += points[1].points  # add DIV points

        if self.ACONF is not None and ps_games.ACONF is not None:
            if self.ACONF == ps_games.ACONF.game_winner():
                score += points[0].points  # add CONF points

        if self.NCONF is not None and ps_games.NCONF is not None:
            if self.NCONF == ps_games.NCONF.game_winner():
                score += points[0].points  # add CONF points

        if self.SB is not None and ps_games.SB is not None:
            if self.SB == ps_games.SB.game_winner():
                score += points[2].points  # add SB points

        self.pick_score = score
        self.save()
        return score

    def points_rem(self):
        rem = 0
        year = Season.objects.get(current=True)
        games = PostSeason.objects.get(year=year)
        points = PostPoint.objects.all().order_by('id')

        if games.get_losers():  # only process if there are at least 1 loser so far
            if self.AWC45 is not None and (games.AWC45 is None or games.AWC45.status[:1] != 'F'):
                rem += points[0].points  # add WC points

            if self.AWC36 is not None and (games.AWC36 is None or games.AWC36.status[:1] != 'F'):
                rem += points[0].points  # add WC points

            if self.NWC45 is not None and (games.NWC45 is None or games.NWC45.status[:1] != 'F'):
                rem += points[0].points  # add WC points

            if self.NWC36 is not None and (games.NWC36 is None or games.NWC36.status[:1] != 'F'):
                rem += points[0].points  # add WC points

            if self.ADIV1 is not None and (games.ADIV1 is None or games.ADIV1.status[:1] != 'F'):
                if self.ADIV1 not in games.get_losers():
                    rem += points[1].points  # add DIV points

            if self.ADIV2 is not None and (games.ADIV2 is None or games.ADIV2.status[:1] != 'F'):
                if self.ADIV2 not in games.get_losers():
                    rem += points[1].points  # add DIV points

            if self.NDIV1 is not None and (games.NDIV1 is None or games.NDIV1.status[:1] != 'F'):
                if self.NDIV1 not in games.get_losers():
                    rem += points[1].points  # add DIV points

            if self.NDIV2 is not None and (games.NDIV2 is None or games.NDIV2.status[:1] != 'F'):
                if self.NDIV2 not in games.get_losers():
                    rem += points[1].points  # add DIV points

            if self.ACONF is not None and (games.ACONF is None or games.ACONF.status[:1] != 'F'):
                if self.ACONF not in games.get_losers():
                    rem += points[2].points  # add DIV points

            if self.NCONF is not None and (games.NCONF is None or games.NCONF.status[:1] != 'F'):
                if self.NCONF not in games.get_losers():
                    rem += points[2].points  # add DIV points

            if self.SB is not None and (games.SB is None or games.SB.status[:1] != 'F'):
                if self.SB not in games.get_losers():
                    rem += points[3].points  # add DIV points

        return rem


class PostPoint(models.Model):
    class Meta:
        verbose_name = 'post season point'
        verbose_name_plural = 'post season points'
        indexes = [models.Index(fields=['gt'])]
        ordering = ['gt']
        constraints = [models.UniqueConstraint(fields=['gt'], name='gt_pts')]

    gt = models.CharField(max_length=3, null=True)  # game type; WC, DIV, CON, SB
    points = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.points)
