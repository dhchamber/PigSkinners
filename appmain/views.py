from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate  # new
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Case, When, Sum, F, Q, IntegerField, FloatField, ExpressionWrapper
from appmain.forms import SignUpForm, ProfileForm, PostPickForm, WeekForm
from django.contrib.auth.forms import AdminPasswordChangeForm  # PasswordChangeForm requires old password
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.utils.decorators import method_decorator
from .tables import SeasonTable
from django_tables2 import SingleTableView  # django-tables2 readthedocs.io
from django.views.generic import ListView, CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse, reverse_lazy
from django.db import transaction
import pytz
import logging

from appmain.models import Season, Week, Pick, Team, Game, Profile, PostPick, PostSeason, PickRevision
from appmain.load_nflgames import load_season, load_score
from appmain.task import load_scores, close_curr_week

# from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.forms import UserCreationForm  # new
# from django.http import HttpResponseRedirect, HttpResponse
# from django.urls import reverse, reverse_lazy
# from django.views.generic import ListView, CreateView
# from django.db import transaction
# from django.template.defaultfilters import floatformat
# from .tables import TeamTable, GameTable, PickGameTable
# from django.template.defaultfilters import floatformat

logger = logging.getLogger(__name__)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = AdminPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AdminPasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


@login_required
def user_profile(request):
    submitted = False
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('/user/profile/?submitted=True')
    else:
        user = User.objects.get(pk=request.user.id)
        form = ProfileForm(instance=profile)
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'appmain/user_profile.html', {'form': form, 'submitted': submitted})


# new signup form
@login_required
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'appmain/signup.html', {'form': form})


def get_selected_week(request):
    year = Season.objects.get(current=True)
    curr_week = year.current_week()
    week_no = request.session.get('week', curr_week.week_no)
    gt = request.session.get('gt', curr_week.gt)
    try:
        wk = Week.objects.get(year=year, week_no=week_no, gt=gt)
    except Week.DoesNotExist:
        wk = Week.objects.get(year=year, week_no=1, gt=gt)

    return wk


def get_postseason_weeks():
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year, gt='POST')

    return weeks


def action_week(request):
    if request.GET.get('btnSetPre1'):
        request.session['week'] = 1
        request.session['gt'] = 'PRE'
    if request.GET.get('btnSetPre2'):
        request.session['week'] = 2
        request.session['gt'] = 'PRE'
    if request.GET.get('btnSetPre3'):
        request.session['week'] = 3
        request.session['gt'] = 'PRE'
    if request.GET.get('btnSetPre4'):
        request.session['week'] = 4
        request.session['gt'] = 'PRE'

    if request.GET.get('btnSetWeek1'):
        request.session['week'] = 1
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek2'):
        request.session['week'] = 2
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek3'):
        request.session['week'] = 3
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek4'):
        request.session['week'] = 4
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek5'):
        request.session['week'] = 5
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek6'):
        request.session['week'] = 6
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek7'):
        request.session['week'] = 7
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek8'):
        request.session['week'] = 8
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek9'):
        request.session['week'] = 9
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek10'):
        request.session['week'] = 10
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek11'):
        request.session['week'] = 11
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek12'):
        request.session['week'] = 12
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek13'):
        request.session['week'] = 13
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek14'):
        request.session['week'] = 14
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek15'):
        request.session['week'] = 15
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek16'):
        request.session['week'] = 16
        request.session['gt'] = 'REG'
    elif request.GET.get('btnSetWeek17'):
        request.session['week'] = 17
        request.session['gt'] = 'REG'

    elif request.GET.get('btnSetWeekPS'):
        request.session['week'] = 18
        request.session['gt'] = 'POST'

    url = request.GET.get('next', '/')
    return redirect(url)


def random_picks(request):
    url = request.GET.get('next', '/')
    return redirect(url)


# setup/games
@staff_member_required
def games_view(request):
    timezone.activate(pytz.timezone('America/Denver'))
    if request.method == 'POST' and 'btnLoadSeason' in request.POST:
        load_season((request.POST.get('txtYear')))
        request.method = 'GET'
        # return redirect(games_view)
        return redirect('setup_games')

    elif request.method == 'POST' and 'btnLoadWeeks' in request.POST:
        year = Season.objects.get(year=request.POST.get('txtYear'))
        year.set_season_weeks()
        return redirect('setup_games')

    elif request.method == 'POST' and 'btnLoadLive' in request.POST:
        load_score('LIVE')
        return redirect('setup_games')
    elif request.method == 'POST' and 'btnLoadWeek' in request.POST:
        year = Season.objects.get(current=True)
        week_no = request.session.get('week', 1)
        gt = request.session.get('gt', 'REG')
        load_score('WEEK', year, gt, week_no)
        return redirect('setup_games')
    elif request.method == 'POST' and 'btntask' in request.POST:
        load_scores('LIVE')
        return redirect('setup_games')
    elif request.method == 'POST' and 'btnCloseWeek' in request.POST:
        close_curr_week(repeat=60)
        return redirect('setup_games')
    else:
        year = Season.objects.get(current=True)
        week_no = request.session.get('week', 1)
        gt = request.session.get('gt', 'REG')
        weeks = Week.objects.filter(year=year, week_no=week_no, gt=gt)
        games = Game.objects.filter(week__in=weeks)
        return render(request, 'appmain/games_view.html', {'games': games})


@login_required
def home(request):
    timezone.activate(pytz.timezone('America/Denver'))
    fav_team = pts_game = None
    try:
        year = Season.objects.get(current=True)
        week = year.current_week()
    except Season.DoesNotExist:
        week = None
        return render(request, 'appmain/home_frame.html')

    pick = Pick.objects.get_or_create(request.user, week)

    if Profile.objects.get(user=request.user).favorite_team is not None:
        fav_team = Profile.objects.get(user=request.user).favorite_team
    elif week is not None and Game.objects.get(week=week, points_game=True) is not None:
        pts_game = Game.objects.get(week=week, points_game=True)
    else:
        fav_team = Team.objects.get(team_abrev='DEN')

    return render(request, 'appmain/home.html', {'week': week, 'fav_team': fav_team, 'pts_game': pts_game, 'pick': pick})


@login_required
def pick_revision(request):
    week = get_selected_week(request)

    # what if no pick revisions exist?  is that a problem?
    # week.create_picks()

    games = Game.objects.filter(week=week).annotate(
        h_pick=Count(Case(When(pick_game__team=F('home_team'), then=1), output_field=IntegerField(), ))) \
        .annotate(
        v_pick=Count(Case(When(pick_game__team=F('visitor_team'), then=1), output_field=IntegerField(), )))
    num_games = games.count() + 1

    user_picks = PickRevision.objects.filter(wk=week,user=request.user).annotate(
        score=Sum(Case(When(pickrevgame__status='W', then=1), default=0, output_field=IntegerField(), )))

    return render(request, 'appmain/pick_revision.html', {'user_picks': user_picks, 'games': games, 'num_games': num_games})



@staff_member_required
def teams_view(request):
    teams = Team.objects.all()
    return render(request, 'appmain/teams_view.html', {'teams': teams})


@staff_member_required
def setup_weeks(request):
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year)
    if request.method == 'POST':
        for week in weeks:
            closed = request.POST.get('chkClosed' + str(week.week_no))
            if closed == 'on':
                closed = True
            else:
                closed = False

            logger.debug(f'Week: {week.week_no} {week.closed}')
            week.closed = closed
            week.save()

    return render(request, 'appmain/setup_weeks.html', {'weeks': weeks})


# @staff_member_required
# def setup_weeks(request):
#     year = Season.objects.get(current=True)
#     weeks = Week.objects.filter(year=year)
#     if request.method == 'POST':
#         form = WeekForm(request.POST, instance=weeks)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Week successfully updated!')
#             return redirect('setup_weeks')
#         else:
#             messages.error(request, 'Please correct the error below.')
#     else:
#         form = WeekForm(instance=weeks.first())
#     return render(request, 'appmain/setup_weeks.html', {'form': form})


@login_required
def pick_view(request):
    timezone.activate(pytz.timezone('America/Denver'))

    year = Season.objects.get(current=True)
    week_no = request.session.get('week', 1)
    gt = request.session.get('gt', 'REG')
    if gt == 'PRE' or gt == 'REG':
        try:
            week = Week.objects.get(year=year, week_no=week_no, gt=gt)
        except Week.DoesNotExist:
            week = Week.objects.get(year=year, week_no=1, gt=gt)

        pick = Pick.objects.get_or_create(request.user, week)
        # try:
        #     pick = Pick.objects.get(user=request.user, wk=week)
        # except Pick.DoesNotExist:
        #     pick = Pick.objects.create_pick(user=request.user, week=week)

        return render(request, 'appmain/pick_view.html', {'pick': pick})
    elif gt == 'POST':
        return redirect('pick_make_ps')


@login_required
def pick_make(request):
    logger.debug('Starting pick_make: ' + request.user.username)
    timezone.activate(pytz.timezone('America/Denver'))
    submitted = False
    week = get_selected_week(request)

    validated = True
    if week.closed:
        return redirect('pick_view')
    else:
        close = week.close_week(request.user)
        print(f'Week closed for week ID: {week.id}')
        logger.debug(f'Week closed for week ID: {week.id}')

    if request.method == 'POST':
        pick_id = request.POST.get("hidPickID")
        pick = Pick.objects.get(pk=pick_id)
        try:
            pts = int(request.POST.get("txtPointsTotal"))
            assert pts > 0
            pick.points = pts
        except AssertionError:
            messages.warning(request, 'Invalid value for points game. Must be greater than zero.')
            validated = False

        if pick.koth_eligible():
            try:
                pick.koth_team = Team.objects.get(id=request.POST.get("cboKingOfHillPick"))
            except Team.DoesNotExist:
                validated = False
                messages.warning(request, 'Failed Validate of KOTH Team: {request.POST.get("cboKingOfHillPick")}')
        try:
            pick.koth_game = (Game.objects.filter(week=pick.wk, home_team=pick.koth_team)
                              | Game.objects.filter(week=pick.wk, visitor_team=pick.koth_team)).first()
        except Game.DoesNotExist:
            messages.warning(request, 'Failed Validate of KOTH Game on Pick ID: {request.POST.get("hidPickID")}')
            validated = False

        for i, pg in enumerate(pick.pickgame_set.all(), start=1):
            team_id = request.POST.get("Selected" + str(i))
            try:
                team = Team.objects.get(id=team_id)
                pg.team = team
                pg.save()
            except Team.DoesNotExist:
                messages.warning(request, 'Failed Validate of Game {i} on Pick ID: {request.POST.get("hidPickID")}')
                validated = False

        if validated:
            pick.saved = True
            pick.save()
            PickRevision.objects.create_rev(pick)
            messages.success(request, 'Your Picks have been saved!')
        else:
            pick.saved = False
            messages.warning(request, 'Please correct the errors below:')
            pick.save()
        return redirect('pick_make')
    else:
        pick = Pick.objects.get_or_create(request.user, week)
        # try:
        #     pick = Pick.objects.get(user=request.user, wk=week)
        # except Pick.DoesNotExist:
        #     pick = Pick.objects.create_pick(user=request.user, week=week)

        if 'submitted' in request.GET:
            submitted = True

        return render(request, 'appmain/pick_make.html', {'pick': pick, 'submitted': submitted})


@login_required
def pick_make_ps(request):
    timezone.activate(pytz.timezone('America/Denver'))
    year = Season.objects.get(current=True)
    weeks = get_postseason_weeks()
    post_season = PostSeason.objects.get(year=year)
    post_pick = PostPick.objects.get_or_create(request.user, year)

    # try:
    #     post_pick = PostPick.objects.get(year=year, user=request.user)
    #     print(f'Got Pick: {post_pick.id}')
    # except PostPick.DoesNotExist:
    #     post_pick = PostPick.objects.create_ps_pick(year=year, user=request.user)
    #     print(f'Created Pick: {post_pick.id}')

    if request.method == 'POST':
        print(f'In Post: {post_pick.user.username}')
        form = PostPickForm(request.POST, instance=post_pick)
        form.fields['entered_by'].required = False
        form.fields['pick_score'].required = False
        # form.data['updated_by'] = request.user
        # print(f'Form: {form.data["entered_by"]}')
        if form.is_valid():
            # form.fields['saved'].initial = 1
            form.save()
            pass  # does nothing, just trigger the validation
        else:
            print(f'Form Errors: {form.errors}')

    else:
        form = PostPickForm(instance=post_pick, initial={'updated_by': request.user, 'saved': True})

    messages.info(request, 'Welcome to the Playoffs!')
    return render(request, 'appmain/pick_make_ps2.html',
                  {'form': form, 'weeks': weeks, 'post_season': post_season})


@login_required
def standing_weekdet(request):
    page = standing_week(request, True)
    return page


@login_required
def standing_weeksum(request):
    page = standing_week(request, False)
    return page


@login_required
def standing_week(request, detail):
    week = get_selected_week(request)

    # loop and create empty picks for each active user if one doesn't exist
    week.create_picks()

    if week.closed:
        if detail:
            games = Game.objects.filter(week=week).annotate(
                h_pick=Count(Case(When(pick_game__team=F('home_team'), then=1), output_field=IntegerField(), ))) \
                .annotate(
                v_pick=Count(Case(When(pick_game__team=F('visitor_team'), then=1), output_field=IntegerField(), )))
            num_games = games.count() + 1
        else:
            games = None
            num_games = 0

        user_picks = Pick.objects.filter(wk=week).annotate(
            score=Sum(Case(When(pickgame__status='W', then=1), default=0, output_field=IntegerField(), )))

        return render(request, 'appmain/standing_week_closed.html',
                      {'user_picks': user_picks, 'games': games, 'num_games': num_games})

    # if week is still open then show users and if picks are saved or not
    else:
        user_picks = Pick.objects.filter(wk=week)
        print(f'ALL: Found picks for  {week.week_no} / {week.id} total: {user_picks.count()}')
        return render(request, 'appmain/standing_week_open.html', {'user_picks': user_picks})


@login_required
def standing_week_prospective(request):
    week = get_selected_week(request)

    # loop and create empty picks for each active user if one doesn't exist
    week.create_picks()

    if week.closed:
        games = Game.objects.filter(week=week).annotate(
            h_pick=Count(Case(When(pick_game__team=F('home_team'), then=1), output_field=IntegerField(), ))) \
            .annotate(
            v_pick=Count(Case(When(pick_game__team=F('visitor_team'), then=1), output_field=IntegerField(), )))
        num_games = games.count() + 1

        # score the game as won if it is done (W) or still in prgress (w)
        user_picks = Pick.objects.filter(wk=week).annotate(
            score=Sum(Case(When(pickgame__status__in=('w', 'W'), then=1), default=0, output_field=IntegerField(), )))
        return render(request, 'appmain/standing_week_prospective.html',
                      {'user_picks': user_picks, 'games': games, 'num_games': num_games})

    # if week is still open then show users and if picks are saved or not
    else:
        user_picks = Pick.objects.filter(wk=week)
        print(f'ALL: Found picks for  {week.week_no} / {week.id} total: {user_picks.count()}')
        return render(request, 'appmain/standing_week_open.html', {'user_picks': user_picks})


@login_required
def standing_koth(request):
    week = get_selected_week(request)
    week.create_picks()

    user_picks = Pick.objects.filter(wk=week)
    if week.closed:
        return render(request, 'appmain/standing_koth.html', {'user_picks': user_picks, 'week': week})
    else:
        return render(request, 'appmain/standing_koth_open.html', {'user_picks': user_picks, 'week': week})


@login_required
def standing_post(request):
    timezone.activate(pytz.timezone('America/Denver'))
    year = Season.objects.get(current=True)
    try:
        games = PostSeason.objects.get(year=year)
    except PostSeason.DoesNotExist:
        return render(request, 'appmain/standing_post.html')

    for user in User.objects.all():
        if user.is_active:
            pick = PostPick.objects.get_or_create(request.user, year)

            # try:
            #     pick = PostPick.objects.get(user=user, year=year)
            # except PostPick.DoesNotExist:
            #     pick = PostPick.objects.create_ps_pick(user=user, year=year)
    picks = PostPick.objects.filter(year=year)

    return render(request, 'appmain/standing_post.html', {'picks': picks, 'games': games})


@login_required
def standing_season(request):
    logger.debug('Starting standing_season: ' + request.user.username)
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year, gt='REG')
    current_week = year.current_week()

    w1 = Week.objects.filter(year=year, gt='REG', week_no__lt=10)
    w2 = Week.objects.filter(year=year, gt='REG', week_no__gt=9)
    logger.debug('Starting standing_season/got w1 & w2: ' + request.user.username)

    game_cnt = Season.objects.filter(current=True) \
        .annotate(half1=Count('weeks__game_wk__gsis', filter=Q(weeks__in=w1))) \
        .annotate(half2=Count('weeks__game_wk__gsis', filter=Q(weeks__in=w2))) \
        .annotate(all=Count('weeks__game_wk__gsis', filter=Q(weeks__in=weeks)))
    logger.debug(f'Starting standing_season/got game_cnts: {request.user.username} {game_cnt[0].half1}')

    users = year.season_scores().annotate(
        perc1=ExpressionWrapper(F('half1') * float(100.0 / game_cnt[0].half1), output_field=FloatField())) \
        .annotate(perc2=ExpressionWrapper(F('half2') * float(100.0 / game_cnt[0].half2), output_field=FloatField())) \
        .annotate(pall=ExpressionWrapper(F('all') * float(100.0 / game_cnt[0].all), output_field=FloatField()))
    logger.debug(f'Starting standing_season/got user subtotals: {users[0].perc1}')

    winners = year.season_winner()
    if current_week.week_no == 9:
        winner = winners['half1']
    elif current_week.week_no == 17:
        winner = winners['half2']
    else:
        winner = User.objects.none()

    #  first make sure picks exist for every user for every week
    #  if picks didn't exist then they didn't get counted above, that is ok,
    #  but they need to exist even if empty for the page display
    for week in weeks:
        week.create_picks()
    logger.debug('Starting standing_season/created picks: ' + request.user.username)

    user_picks = Pick.objects.filter(wk__in=weeks) \
        .annotate(score=Sum(Case(When(pickgame__status='W', then=1), default=0, output_field=IntegerField(), )))
    logger.debug(f'Starting standing_season/got annotated picks: {user_picks}')

    return render(request, 'appmain/standing_season.html',
                  {'weeks': weeks, 'users': users, 'user_picks': user_picks, 'game_cnt': game_cnt, 'winner': winner,
                   'curr_week': current_week})


@method_decorator(staff_member_required, name='dispatch')
class SeasonListView(LoginRequiredMixin, SingleTableView):
    model = Season
    table_class = SeasonTable
    login_required = True
    template_name = 'appmain/setup_season.html'

# class SeasonCreate(CreateView):
#     model = Season
#     template_name = 'appmain/season_create.html'
#     form_class = SeasonForm1
#     # fields = ['year', 'current', 'start_date', 'end_date']
#     success_url = None
#
#     def get_context_data(self, **kwargs):
#         data = super(SeasonCreate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['weeks'] = WeekFormSet(self.request.POST)
#         else:
#             data['weeks'] = WeekFormSet()
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         weeks = context['weeks']
#         with transaction.atomic():
#             form.instance.created_by = self.request.user
#             self.object = form.save()
#             if weeks.is_valid():
#                 weeks.instance = self.object
#                 weeks.save()
#         return super(SeasonCreate, self).form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('appmain:season_detail', kwargs={'pk': self.object.pk})
#
#
# class SeasonUpdate(UpdateView):
#     model = Season
#     # success_url = '/'
#     # fields = ['year', 'current', 'start_date', 'end_date']
#     # template_name = 'appmain/season_create.html'
#     template_name = 'appmain/season_form.html'
#     form_class = SeasonForm
#     success_url = None
#
#     def get_context_data(self, **kwargs):
#         data = super(SeasonUpdate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['weeks'] = WeekFormSet(self.request.POST, instance=self.object)
#         else:
#             data['weeks'] = WeekFormSet(instance=self.object)
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         weeks = context['weeks']
#         with transaction.atomic():
#             form.instance.created_by = self.request.user
#             self.object = form.save()
#             if weeks.is_valid():
#                 weeks.instance = self.object
#                 weeks.save()
#         return super(SeasonUpdate, self).form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('appmain:season_detail', kwargs={'pk': self.object.pk})
#
#
# class SeasonWeekCreate(CreateView):
#     model = Season
#     fields = ['year', 'current', 'start_date', 'end_date']
#     success_url = reverse_lazy('season-list')
#
#     def get_context_data(self, **kwargs):
#         data = super(SeasonWeekCreate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['weeks'] = WeekFormSet(self.request.POST)
#         else:
#             data['weeks'] = WeekFormSet()
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         weeks = context['weeks']
#         with transaction.atomic():
#             self.object = form.save()
#
#             if weeks.is_valid():
#                 weeks.instance = self.object
#                 weeks.save()
#         return super(SeasonWeekCreate, self).form_valid(form)
#
#
# class SeasonWeekUpdate(UpdateView):
#     model = Season
#     fields = ['year', 'current', 'start_date', 'end_date']
#     success_url = reverse_lazy('season-list')
#
#     def get_context_data(self, **kwargs):
#         data = super(SeasonWeekUpdate, self).get_context_data(**kwargs)
#         if self.request.POST:
#             data['weeks'] = WeekFormSet(self.request.POST, instance=self.object)
#         else:
#             data['weeks'] = WeekFormSet(instance=self.object)
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         weeks = context['weeks']
#         with transaction.atomic():
#             self.object = form.save()
#
#             if weeks.is_valid():
#                 weeks.instance = self.object
#                 weeks.save()
#         return super(SeasonWeekUpdate, self).form_valid(form)
#
#
# class SeasonDelete(DeleteView):
#     model = Season
#     success_url = reverse_lazy('season-list')


# class SeasonList(ListView):
#     model = Season


# replaced by Class SeasonListView
# @login_required
# def setup_season(request):
#     submitted = False
#     # profile = Season.objects.get(user=request.user)
#     years = Season.objects.all()
#     if request.method == 'POST':
#         print(f'POST:', request.POST)
#         form = SeasonForm(request.POST, instance=years)
#         if form.is_valid():
#             form.save()
#             return redirect('/user/profile/?submitted=True')
#     else:
#         years = Season.objects.all()
#         form = SeasonForm(years)
#         if 'submitted' in request.GET:
#             submitted = True
#
#     return render(request, 'appmain/setup_season.html', {'form': form})


# 'submitted': submitted


# @login_required
# def update_profile(request, user_id):
#     user = User.objects.get(pk=user_id)
#     user.profile.bio = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit...'
#     user.save()

# tutorial/views.py
# class GameListView(SingleTableView):
#    model = Game
#    table_class = GameTable
#    template_name = 'appmain/game.html'


# class TeamListView(SingleTableView):
#     model = Team
#     table_class = TeamTable
#     template_name = 'appmain/team.html'


# django-tables2 readthedocs.io

# @login_required
# def picks_view(request):
#    games = Game.objects.filter(wk_id=1).order_by('gsis')
#    return render(request, 'appmain/pick_view.html', {'games': games})

# remove replace with form view and html
# def picks_make(request):
#     return render(request, 'appmain/pick_make.html', {})
