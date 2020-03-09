from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate  # new
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Case, When, Sum, Max, F, Q, IntegerField, FloatField, ExpressionWrapper
from appmain.forms import SignUpForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django_tables2 import SingleTableView  # django-tables2 readthedocs.io
from django.utils import timezone
from django.template.defaultfilters import floatformat
import pytz

from .models import Season, Week, Seed, Pick, Team, Game, PostPick
from .tables import TeamTable, GameTable, PickGameTable
from appmain.load_nflgames import load_week, LoadSeason, load_score

# from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.forms import UserCreationForm  # new
# from django.http import HttpResponseRedirect, HttpResponse
# from django.urls import reverse, reverse_lazy
# from django.views.generic import ListView, CreateView
# from django.db import transaction
# from django.template.defaultfilters import floatformat



def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


# tutorial page 1
class GameListView(SingleTableView):
    model = Game
    table_class = GameTable
    template_name = 'appmain/game_view.html'

    def get_recordset(self):
        # week = get_selected_week(request)
        # week = Week.objects.get(week=wk)
        year = Season.objects.get(current=True)
        week = Week.objects.get(year=year, week_no=22, gt="REG")
        return Game.objects.filter(week=week)


# tutorial/views.py
# class GameListView(SingleTableView):
#    model = Game
#    table_class = GameTable
#    template_name = 'appmain/game.html'


class TeamListView(SingleTableView):
    model = Team
    table_class = TeamTable
    template_name = 'appmain/team.html'


# django-tables2 readthedocs.io

def get_selected_week(request):
    year = Season.objects.get(current=True)
    week_no = request.session.get('week', 1)
    gt = request.session.get('gt', 'REG')
    try:
        wk = Week.objects.get(year=year, week_no=week_no, gt=gt)
    except:
        wk = Week.objects.get(year=year, week_no=1, gt=gt)
    # print(f'Found Week # {wk.week_no} loaded for year {year.year}')

    return wk


def get_postseason_weeks(request):
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
    print(f'NEXT: from GET: {url}')
    return redirect(url)


def random_picks(request):
    url = request.GET.get('next', '/')
    return redirect(url)


# tutorial page 2 - QuerySets
# takes table GameTable based on model Game
@login_required
def game_list(request):
    if request.method == 'POST' and 'btnLoadSeason' in request.POST:
        LoadSeason((request.POST.get('txtYear')))
    elif request.method == 'POST' and 'btnLoadWeek' in request.POST:
        load_week()
    elif request.method == 'POST' and 'btnLoadLive' in request.POST:
        load_score('REG')
    else:
        # week = Week.objects.get(week_no=15)
        # table = GameTable(Game.objects.filter(week=week))
        table = GameTable(Game.objects.all())
        # return render(request, "appmain/game.html",{"table" : table})

    return redirect('setup_games')


# setup/games
@login_required
def games_view(request):
    timezone.activate(pytz.timezone('America/Denver'))
    if request.method == 'POST' and 'btnLoadSeason' in request.POST:
        LoadSeason((request.POST.get('txtYear')))
        request.method = 'GET'
        return redirect(games_view)

    elif request.method == 'POST' and 'btnLoadWeeks' in request.POST:
        load_week()
        return redirect('setup_games')

    elif request.method == 'POST' and 'btnLoadLive' in request.POST:
        load_score('LIVE')
        return redirect('setup_games')

    elif request.method == 'POST' and 'btnLoadWeek' in request.POST:
        year = Season.objects.get(current=True)
        week_no = request.session.get('week', 1)
        gt = request.session.get('gt', 'REG')
        load_score('WEEK',year, gt, week_no)
        return redirect('setup_games')
    else:
        year = Season.objects.get(current=True)
        week_no = request.session.get('week', 1)
        gt = request.session.get('gt', 'REG')
        weeks = Week.objects.filter(year=year, week_no= week_no, gt=gt)
        # weeks = Week.objects.filter(year=year, gt='POST')
        # print(f'Found Week # {week.week_no} loaded for year {year.year}')
        games = Game.objects.filter(week__in=weeks)
        print(f'Found games # {games.count()} ')
        return render(request, 'appmain/games_view.html', {'games': games})

    # return redirect('setup_games')


#       return render(request, 'appmain/new_games.html', {'games': games})


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


@login_required
def update_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user.profile.bio = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit...'
    user.save()


# @login_required
# def post_list(request):
#     return render(request, 'appmain/post_list.html', {})


@login_required
def home(request):
    timezone.activate(pytz.timezone('America/Denver'))
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year,gt='REG')
    return render(request, 'appmain/home.html', {'weeks': weeks})


# @login_required
# def picks_view(request):
#    games = Game.objects.filter(wk_id=1).order_by('gsis')
#    return render(request, 'appmain/pick_view.html', {'games': games})

# remove replace with form view and html
# def picks_make(request):
#     return render(request, 'appmain/pick_make.html', {})


@login_required
def pick_revision(request):
    # if not request.user.is_authenticated:
    #    return redirect('%s?next=%s' %(settings.LOGIN_URL, request.path))
    return render(request, 'appmain/pick_revision.html', {})


@login_required
def teams_view(request):
    teams = Team.objects.all()
    return render(request, 'appmain/teams_view.html', {'teams': teams})


@login_required
def setup_weeks(request):
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year)
    return render(request, 'appmain/setup_weeks.html', {'weeks': weeks})


# @login_required
def pick_view(request):
    timezone.activate(pytz.timezone('America/Denver'))

    year = Season.objects.get(current=True)
    week_no = request.session.get('week', 1)
    gt = request.session.get('gt', 'REG')
    if gt == 'PRE' or gt == 'REG':
        try:
            week = Week.objects.get(year=year, week_no=week_no, gt=gt)
        except:
            week = Week.objects.get(year=year, week_no=1, gt=gt)

        try:
            pick = Pick.objects.get(user=request.user, wk=week)
        except:  # TODO: get exception type
            pick = Pick.objects.create_pick(user=request.user, week=week)

        return render(request, 'appmain/pick_view.html', {'pick': pick})
    elif gt == 'POST':
        return redirect('pick_make_ps')


@login_required
def pick_make(request):
    timezone.activate(pytz.timezone('America/Denver'))
    submitted = False
    wk = get_selected_week(request)

    validated = True
    # if not wk.closed:
    #    close = wk.close_week(request.user)
    # print(f'Week closed for week ID: {wk.id}')

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

        try:
            pick.koth_team = Team.objects.get(id=request.POST.get("cboKingOfHillPick"))
        except:
            validated = False
            messages.warning(request, 'Failed Validate of KOTH Team: {request.POST.get("cboKingOfHillPick")}')
            print(f'Failed Validate of KOTH Team on Pick ID: {request.POST.get("hidPickID")}')
        try:
            pick.koth_game = (
                        Game.objects.filter(week=pick.wk, home_team=pick.koth_team) | Game.objects.filter(week=pick.wk,
                                                                                                          visitor_team=pick.koth_team)).first()
        except:
            messages.warning(request, 'Failed Validate of KOTH Game on Pick ID: {request.POST.get("hidPickID")}')
            print(f'Failed Validate of KOTH Game on Pick ID: {request.POST.get("hidPickID")}')
            validated = False

        for i, pg in enumerate(pick.pickgame_set.all(), start=1):
            team_id = request.POST.get("Selected" + str(i))
            print(f'Setting game for: {i} as Team: {team_id}')
            try:
                team = Team.objects.get(id=team_id)
                pg.team = team
                pg.save()
            except:
                messages.warning(request, 'Failed Validate of Game {i} on Pick ID: {request.POST.get("hidPickID")}')
                print(f'Failed Validate of Game {i} on Pick ID: {request.POST.get("hidPickID")}')
                validated = False


        if validated:
            pick.saved = True
            pick.save()
            messages.success(request, 'Your Picks have been saved!')
            print(f'SAVED on Pick ID: {request.POST.get("hidPickID")}')
        else:
            pick.saved = False
            messages.warning(request,'Please correct the errors below:')
            print(f'NOT saved on Pick ID: {request.POST.get("hidPickID")}')

        return redirect('pick_make')
    else:
        try:
            pick = Pick.objects.get(user=request.user, wk=wk)
            # print(f'found pick for  {request.user.username} / {request.user.id} pick: {pick.id}')
        except:
            pick = Pick.objects.create_pick(user=request.user, week=wk)
            # print(f'Created pick for  {request.user.username} / {request.user.id} pick: {pick.id}')

        if 'submitted' in request.GET:
            submitted = True

        return render(request, 'appmain/pick_make.html', {'pick': pick, 'submitted': submitted})


@login_required
def pick_make_ps(request):
    timezone.activate(pytz.timezone('America/Denver'))
    year = Season.objects.get(current=True)
    weeks = get_postseason_weeks(request)

#TODO: loop and check for user post season picks create if necessary
    try:
        pick = PostPick.objects.get(user=request.user)
        print(f'found pick for  {request.user.username} / {request.user.id} pick: {pick.id}')
    except:
        pick = PostPick.objects.create_ps_pick(user=request.user)
        print(f'Created pick for  {request.user.username} / {request.user.id} pick: {pick.id}')

    afc = {}
    nfc = {}
    seeds = Seed.objects.filter(year=year)
    for seed in seeds:
        if seed.team.conference == "AFC":
            afc[seed.seed] = seed.team
        else:
            nfc[seed.seed] = seed.team
#TODO: add lookup to get game for each seed and add to afc and nfc dicts
    return render(request, 'appmain/pick_make_ps.html', {'pick': pick, 'weeks': weeks, 'seeds':seeds, 'afc':afc, 'nfc':nfc})

@login_required
def pick_save_ps(request):

    if request.method == 'POST':
#TODO: validate pick data is complete and return message if not
        pick_id = request.POST.get("hidPickID")
        print(f'Pick ID: {pick_id}')
        pick = PostPick.objects.get(id=pick_id)
        pick.updated_by = request.user
        try:
            pts = int(request.POST.get("bowlPoints"))
            assert pts > 0
            pick.points = pts
        except AssertionError:
            messages.warning(request, 'Invalid value for points game. Must be greater than zero.')
            validated = False
        for i, game in enumerate(pick.post_games.all(), start=1):
            ps_type = game.ps_type[7:]
            print(f'Setting game for: {i} as Type: {ps_type}')
            team_id = request.POST.get('hid'+ps_type)
            print(f'Setting game for: {i} as Team: {team_id}')
            try:
                team = Team.objects.get(id=team_id)
            except:
                messages.warning(request, 'Failed Validate of Game {i}/team ID: {team_id} on Pick ID: {pick_id}')
                print(f'Failed Validate of Game {i} on Pick ID: {request.POST.get("hidPickID")}')
                validated = False

            game.team = team
            game.save()

        pick.saved = True
        pick.save()
    return redirect('pick_make_ps')


@login_required
def standing_weekdet(request):
    page = standing_week(request,True)
    return page

@login_required
def standing_weeksum(request):
    page = standing_week(request,False)
    return page

@login_required
def standing_week(request, detail):
    wk = get_selected_week(request)

    # loop and create empty picks for each active user if one doesn't exist
    # TODO: make this a common function
    for user in User.objects.all():
        if user.is_active:
            try:
                pick = Pick.objects.get(user=user, wk=wk)
            except:
                pick = Pick.objects.create_pick(user=user, week=wk)

    # if wk.closed:
        if detail:
            games = Game.objects.filter(week=wk).annotate(
                h_pick=Count(Case(When(pick_game__team=F('home_team'), then=1), output_field=IntegerField(), ))) \
                .annotate(
                v_pick=Count(Case(When(pick_game__team=F('visitor_team'), then=1), output_field=IntegerField(), )))
            num_games = games.count() + 1
        else:
            games = None
            num_games = 0

        user_picks = Pick.objects.filter(wk=wk).annotate(
            score=Sum(Case(When(pickgame__status='W', then=1), default=0, output_field=IntegerField(), )))

        return render(request, 'appmain/standing_week_closed.html',
                      {'user_picks': user_picks, 'games': games, 'num_games': num_games})

    # if week is still open then show users and if picks are saved or not
    # else:
    #     user_picks = Pick.objects.filter(wk=wk)
    #     print(f'ALL: Found picks for  {wk.week_no} / {wk.id} total: {user_picks.count()}')
    #     return render(request, 'appmain/standing_week_open.html', {'user_picks': user_picks})
        # pass


@login_required
def standing_week_prospective(request):
    wk = get_selected_week(request)

    # loop and create empty picks for each active user if one doesn't exist
    # TODO: make this a common function
    for user in User.objects.all():
        if user.is_active:
            try:
                pick = Pick.objects.get(user=user, wk=wk)
            except:
                pick = Pick.objects.create_pick(user=user, week=wk)

    # if wk.closed:
        games = Game.objects.filter(week=wk).annotate(
            h_pick=Count(Case(When(pick_game__team=F('home_team'), then=1), output_field=IntegerField(), ))) \
            .annotate(
            v_pick=Count(Case(When(pick_game__team=F('visitor_team'), then=1), output_field=IntegerField(), )))
        num_games = games.count() + 1

        # score the game as won if it is done (W) or still in prgress (w)
        user_picks = Pick.objects.filter(wk=wk).annotate(
            score=Sum(Case(When(pickgame__status__in=('w','W'), then=1), default=0, output_field=IntegerField(), )))
        # TODO: add something to html to show the game status and highlight winning from won
        return render(request, 'appmain/standing_week_prospective.html',
                      {'user_picks': user_picks, 'games': games, 'num_games': num_games})

    # if week is still open then show users and if picks are saved or not
    # else:
    #     user_picks = Pick.objects.filter(wk=wk)
    #     print(f'ALL: Found picks for  {wk.week_no} / {wk.id} total: {user_picks.count()}')
    #     return render(request, 'appmain/standing_week_open.html', {'user_picks': user_picks})


def standing_koth(request):
    wk = get_selected_week(request)
    for user in User.objects.all():
        if user.is_active:
            try:
                pick = Pick.objects.get(user=user, wk=wk)
            except:
                pick = Pick.objects.create_pick(user=user, week=wk)

    user_picks = Pick.objects.filter(wk=wk)

    return render(request, 'appmain/standing_koth.html', {'user_picks': user_picks})


def standing_post(request):
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year,gt='POST')
    games = Game.objects.filter(week__in=weeks)

    for user in User.objects.all():
        if user.is_active:
            try:
                pick = PostPick.objects.get(user=user, year=Season.objects.get(current=True))
            except:
                pick = PostPick.objects.create_ps_pick(user=user)
    picks = PostPick.objects.filter(year=Season.objects.get(current=True))
#TODO: calc score and points remaining for each user

    return render(request, 'appmain/standing_post.html', {'picks': picks,'games':games})


def standing_season(request):
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year,gt='REG')
    curr_week = year.curr_week()

    w1 = Week.objects.filter(year=year, gt='REG', week_no__lt=10)
    w2 = Week.objects.filter(year=year, gt='REG', week_no__gt=9)

    game_cnt = Season.objects.filter(current=True)\
        .annotate(half1=Count('weeks__game_wk__gsis',filter=Q(weeks__in=w1)))\
        .annotate(half2=Count('weeks__game_wk__gsis', filter=Q(weeks__in=w2)))\
        .annotate(all=Count('weeks__game_wk__gsis', filter=Q(weeks__in=weeks)))

    users = year.season_scores().annotate(perc1=ExpressionWrapper(F('half1') * float(100.0 / game_cnt[0].half1), output_field=FloatField()))\
                                .annotate(perc2=ExpressionWrapper(F('half2')*float(100.0/game_cnt[0].half2),output_field=FloatField()))\
                                .annotate(pall=ExpressionWrapper(F('all')*float(100.0/game_cnt[0].all),output_field=FloatField()))

    winners = year.season_winner()
    if curr_week.week_no <= 9:
        winner = winners['half1']
    else:
        winner = winners['half2']
    # for user in winners['half1']:
    #     print(f'half1 winner(s): {user.last_name}')
    #
    # for user in winners['half2']:
    #     print(f'half2 winner(s): {user.last_name}')
    #
    # for user in winners['all']:
    #     print(f'overall winner(s): {user.last_name}')

    #  first make sure picks exist for every user for every week
    #  if picks didn't exist then they didn't get counted above, that is ok, but they need to exist even if empty for the page display
    for user in users:
        print(f'user: {user.last_name} half1: {user.half1} games: {game_cnt[0].half1} perc1: {user.perc1} ')
        for week in weeks:
            # try:
                p = Pick.objects.filter(user=user,wk=week)
                if p.count() == 0:
                    Pick.objects.create_pick(user=user, week=week)

    user_picks = Pick.objects.filter(wk__in=weeks)\
            .annotate(score=Sum(Case(When(pickgame__status='W', then=1), default=0, output_field=IntegerField(), )))

    # return render(request, 'appmain/standing_season.html', {'weeks': weeks, 'user_picks': user_picks, 'game_cnt': game_cnt,
    #                'win_subtot1': win_subtot1, 'win_perc1': win_perc1, 'win_subtot2': win_subtot2, 'win_perc2': win_perc2, 'win_total': win_total, 'win_totalperc': win_totalperc})
    return render(request, 'appmain/standing_season.html', {'weeks': weeks, 'users':users, 'user_picks': user_picks, 'game_cnt': game_cnt, 'winner': winner, 'curr_week': curr_week})