from django.shortcuts import render, redirect  # add redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate  # new
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm  # new
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView
from django.db import transaction
from django.db.models import Sum
from appmain.forms import SignUpForm, PickForm, PickGameForm, GamePickFormSet
from django_tables2 import SingleTableView # django-tables2 readthedocs.io
from django.utils import timezone
import pytz

from .models import Season, Week, Pick, Team, Game, PickGame
from .tables import TeamTable, GameTable  # tutorial page 2 - QuerySets [implied] + django-tables2 readthedocs.io
from appmain.load_nflgames import LoadWeek, LoadSeason, live_scores_reg

# tutorial page 1
#TODO: add login security
class GameListView(ListView):
   model = Game
   template_name = 'appmain/game.html'

   def get_queryset(self):
      week = Week.objects.get(week_no=15)
      return Game.objects.filter(week=week)  # week 17 games


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

def action_week(request):
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

   next = request.GET.get('next','/')
   print(f'NEXT: from GET: {next}')
   # print(f'Path from request: {request.META.get("HTTP_REFFERER")}')
   # print(f'Path_info from request: {request.path_info}')
   # print(f'Path_info from request: {request.build_absolute_url()}')
   # print(f'Path_info from request: {request.get_full_path()}')
   return redirect(next)
   # HttpResponseRedirect(next)


def random_picks(request):


   next = request.GET.get('next','/')
   return redirect(next)

# tutorial/views.py
# class GameListView(SingleTableView):
#    model = Game
#    table_class = GameTable
#    template_name = 'appmain/game.html'

# tutorial page 2 - QuerySets
# takes table GameTable based on model Game
@login_required
def game_list(request):
   if request.method == 'POST' and 'btnLoadSeason' in request.POST:
      LoadSeason((request.POST.get('txtYear')))
      #return user to page
      # return HttpResponseRedirect(home(request))
   elif request.method == 'POST' and 'btnLoadWeek' in request.POST:
      LoadWeek()
      # return HttpResponseRedirect(reverse(game_list(request)))
   elif request.method == 'POST' and 'btnLoadLive' in request.POST:
      live_scores_reg()
      # return HttpResponseRedirect(reverse(game_list(request)))
   else:
      # week = Week.objects.get(week_no=15)
      # table = GameTable(Game.objects.filter(week=week))
      table = GameTable(Game.objects.all())
      # return render(request, "appmain/game.html",{"table" : table})

   return redirect('setup_games')

# setup/games
@login_required
def games_view(request):
   if request.method == 'POST' and 'btnLoadSeason' in request.POST:
      LoadSeason((request.POST.get('txtYear')))

      # request.method = 'GET'
      # return HttpResponseRedirect(reverse(games_view(request)))
   elif request.method == 'POST' and 'btnLoadWeek' in request.POST:
      LoadWeek()

      # request.method = 'GET'
      # return HttpResponseRedirect(reverse(games_view(request)))
   elif request.method == 'POST' and 'btnLoadLive' in request.POST:
      live_scores_reg()

      # request.method = 'GET'
      # return HttpResponseRedirect(games_view(request))
   else:
      year = Season.objects.get(current=True)
      week = Week.objects.get(year=year, week_no= 1, gt='REG')
      print(f'Found Week # {week.week_no} loaded for year {year.year}')
      games = Game.objects.filter(week=week)
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
   weeks = Week.objects.filter(id=1)
   return render(request, 'appmain/home.html', {'weeks': weeks})


# @login_required
# def picks_view(request):
#    games = Game.objects.filter(wk_id=1).order_by('gsis')
#    return render(request, 'appmain/picks_view.html', {'games': games})

# remove replace with form view and html
# def picks_make(request):
#     return render(request, 'appmain/picks_make.html', {})


@login_required
def picks_revisions(request):
   # if not request.user.is_authenticated:
   #    return redirect('%s?next=%s' %(settings.LOGIN_URL, request.path))
   return render(request, 'appmain/picks_revisions.html', {})


@login_required
def teams_view(request):
   teams = Team.objects.all()
   return render(request, 'appmain/teams_view.html', {'teams': teams})

@login_required
def setup_weeks(request):
   year = Season.objects.get(current=True)
   weeks = Week.objects.filter(year=year)
   return render(request, 'appmain/setup_weeks.html', {'weeks': weeks})


@login_required
def picks_view(request):
   timezone.activate(pytz.timezone('America/Denver'))
   year = Season.objects.get(current=True)
   week_no = request.session.get('week', 1)
   gt = request.session.get('gt', 'REG')
   try:
      wk = Week.objects.get(year=year, week_no=week_no, gt=gt)
   except:
      wk = Week.objects.get(year=year, week_no=1, gt='REG')

   try:
      pick = Pick.objects.get(user=request.user, wk=wk)
   except:  #TODO: get exception type
      pass

   # if picks.count() == 0:
   #    pick_wk = Pick()
   #    pick_wk.user = request.user
   #    pick_wk.wk = Week.objects.filter(year=2018,week_no=3)
   #    pick_wk.points = 41
   #    pick_wk.entered_by = request.user
   #    pick_wk.updated_by = request.user
   #    pick_wk.save()
   #    pick_wk = Pick.objects.filter(user = request.user, wk = 3)  # changed from get to filter to avoid "Pick is not iterable" error

   return render(request, 'appmain/picks_view.html', {'pick': pick})

#TODO: add view for Teams list
#TODO: add template too (HTML) for Teams list
#TODO: add link to navbar


# TODO: add validated to logic
# form for user to pick games
@login_required
def picks_make(request):
   timezone.activate(pytz.timezone('America/Denver'))
   submitted = False
   wk = get_selected_week(request)

   validated = True
   # if not wk.closed:
   #    close = wk.close_week(request.user)
      # print(f'Week closed for week ID: {wk.id}')

   print(f'In picks_make : Chosen Week ID: {wk.id} Start_date {wk.start_dt()} Closed: {wk.closed}')

   if request.method == 'POST':
      print(f'of Pick ID: {request.POST.get("hidPickID")}')
      pick_id = request.POST.get("hidPickID")
      pick = Pick.objects.get(pk=pick_id)
      pick.points = request.POST.get("txtPointsTotal")
      try:
         pick.koth_team = Team.objects.get(id=request.POST.get("cboKingOfHillPick"))
      except:
         validated = False
         print(f'Failded Validate of KOTH Team on Pick ID: {request.POST.get("hidPickID")}')
      try:
         pick.koth_game = (Game.objects.filter(week=pick.wk,home_team=pick.koth_team) | Game.objects.filter(week=pick.wk,visitor_team=pick.koth_team)).first()
      except:
         print(f'Failed Validate of KOTH Game on Pick ID: {request.POST.get("hidPickID")}')
         validated = False

      for i, game in enumerate(pick.pickgame_set.all(), start=1):
         team_id = request.POST.get("Selected"+str(i))
         print(f'Setting game for: {i} as Team: {team_id}')
         try:
            team = Team.objects.get(id=request.POST.get("Selected"+str(i)))
         except:
            print(f'Failded Validate of Game {i} on Pick ID: {request.POST.get("hidPickID")}')
            validated = False

         game.team = team
         game.save()

      if validated:
         pick.saved = True
         print(f'SAVED on Pick ID: {request.POST.get("hidPickID")}')
      else:
         pick.saved = False
         print(f'NOT saved on Pick ID: {request.POST.get("hidPickID")}')
      pick.save()

      return redirect('picks_make')
# TODO: change return to same page with picks displayed and "Picks Saved" response
   # sMessage = "Your picks have been saved."
   # sMessage = "This week's picks are closed so your changes can't be saved."

   else:
      # pick, created = Pick.objects.get_or_create(user = request.user, wk = wk, defaults={'user': request.user, 'wk': wk, 'points': 0,'entered_by': request.user, 'updated_by': request.user})
      # #TODO: add check for exception MultipleObjectsReturned  there should be only 1
      # if created:
      #    games = Game.objects.filter(week = wk)
      #    for game in games:
      #       game_picks = PickGame.objects.create(pick_head = pick, game = game, entered_by = request.user, updated_by = request.user)
      #       game_picks.save()
      try:
         pick = Pick.objects.get(user=request.user, wk=wk)
         print(f'found pick for  {request.user.username} / {request.user.id} pick: {pick.id}')
      except:
         pick = Pick.objects.create_pick(user=request.user, week=wk)
         print(f'Created pick for  {request.user.username} / {request.user.id} pick: {pick.id}')

      if 'submitted' in request.GET:
         submitted = True

      # return render(request, 'appmain/picks_make.html', {'form': form, 'submitted': submitted})
      return render(request, 'appmain/picks_make.html', {'pick': pick, 'submitted': submitted})

# class PickList(ListView):
#    model = Pick


def standings_weeksum(request):
   wk = get_selected_week(request)

   # loop and create empty picks for each active user if one doesn't exist
#TODO: make this a common function
   for user in User.objects.all():
      print(f'Found user  {user.username} / {user.id} active: {user.is_active}')
      if user.is_active:
         try:
            pick = Pick.objects.get(user=user, wk=wk)
            print(f'found pick for  {user.username} / {user.id} pick: {pick.id}')
         except:
            pick = Pick.objects.create_pick(user=user, week=wk)
            print(f'Created pick for  {user.username} / {user.id} pick: {pick.id}')

   user_picks = Pick.objects.filter(wk=wk)
   print(f'ALL: Found picks for  {wk.week_no} / {wk.id} total: {user_picks.count()}')
   # if the week is closed then show standings
   if wk.closed:
      games = Game.objects.filter(week=wk)
      num_games = games.count() +1

#TODO: build dictionary, list, ... of games, visitor, home, counts, num games, ...
      # user_picks = Pick.objects.filter(wk=wk) #.values('user').annotate(pick_score=Sum('pickgame__pick_score()'))
      for g in games:
         home = {g: 0}
         visitor = {g: 0}
         for p in user_picks:
            for pg in p.pickgame_set.all():
               if pg.game == g and pg.team == g.home_team:
                  home[g] = home[g] + 1
               elif pg.game == g and pg.team == g.visitor_team:
                  visitor[g] = visitor[g] + 1
         print(f'count for game: {g.home_team} / {g.visitor_team} count: {home[g]}/{visitor[g]}')

      # calculate score for each user
      for user_pick in user_picks:
         user_pick.pick_score = 0
         for game in user_pick.pickgame_set.all():
            user_pick.pick_score += game.pick_score()
         user_pick.save()
      # i = serviceinvoice.objects.annotate(Sum('serviceinvoiceitems__discount_amount')).get(pk=pk)
      # pick_score = PickGame.objects.filter(p)

      return render(request, 'appmain/standings_week_closed.html', {'user_picks': user_picks, 'games':games, 'num_games':num_games, 'home':home, 'visitor':visitor})

   # if week is still open then show users and if picks are saved or not
   else:
      return render(request, 'appmain/standings_week_open.html', {'user_picks': user_picks})
      # pass

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

