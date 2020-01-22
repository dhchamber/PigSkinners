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

# django-tables2 readthedocs.io
#TODO: add login security
class TeamListView(SingleTableView):
   model = Team
   table_class = TeamTable
   template_name = 'appmain/team.html'


@login_required
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

   return redirect('picks_make')


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
      return HttpResponseRedirect(home(request))
   elif request.method == 'POST' and 'btnLoadWeek' in request.POST:
      LoadWeek()
      return HttpResponseRedirect(reverse(game_list(request)))
   elif request.method == 'POST' and 'btnLoadLive' in request.POST:
      live_scores_reg()
      return HttpResponseRedirect(reverse(game_list(request)))
   else:
      # week = Week.objects.get(week_no=15)
      # table = GameTable(Game.objects.filter(week=week))
      table = GameTable(Game.objects.all())
      return render(request, "appmain/game.html",{"table" : table})


@login_required
def games_view(request):
   if request.method == 'POST' and 'btnLoadSeason' in request.POST:
      LoadSeason((request.POST.get('txtYear')))

      request.method = 'GET'
      return HttpResponseRedirect(reverse(games_view(request)))
   elif request.method == 'POST' and 'btnLoadWeek' in request.POST:
      LoadWeek()

      request.method = 'GET'
      return HttpResponseRedirect(reverse(games_view(request)))
   elif request.method == 'POST' and 'btnLoadLive' in request.POST:
      live_scores_reg()

      request.method = 'GET'
      return HttpResponseRedirect(games_view(request))
   else:
      year = Season.objects.get(current=True)
      week = Week.objects.get(year=year, week_no= 1, gt='REG')
      print(f'Found Week # {week.week_no} loaded for year {year.yr}')
      games = Game.objects.filter(week=week)
      print(f'Found games # {games.count()} ')
   return render(request, 'appmain/games_view.html', {'games': games})
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

@login_required
def post_list(request):
    return render(request, 'appmain/post_list.html', {})


@login_required
def home(request):
   weeks = Week.objects.filter(id=1)
   return render(request, 'appmain/home.html', {'weeks': weeks})


@login_required
def picks_view(request):
   games = Game.objects.filter(wk_id=1).order_by('gsis')
   return render(request, 'appmain/picks_view.html', {'games': games})

# remove replace with form view and html
# def picks_make(request):
#     return render(request, 'appmain/picks_make.html', {})


@login_required
def picks_revisions(request):
    return render(request, 'appmain/picks_revisions.html', {})


@login_required
def teams_view(request):
   teams = Team.objects.all()
   return render(request, 'appmain/teams_view.html', {'teams': teams})



@login_required
def picks_view(request):
   # try:
   picks = Pick.objects.filter(user = request.user, wk = 3)  # changed from get to filter to avoid "Pick is not iterable" error
   # except Pick.DoesNotExist:
   if picks.count() == 0:
      pick_wk = Pick()
      pick_wk.user = request.user
      pick_wk.wk = Week.objects.filter(year=2018,week_no=3)
      pick_wk.points = 41
      pick_wk.entered_by = request.user
      pick_wk.updated_by = request.user
      pick_wk.save()
      pick_wk = Pick.objects.filter(user = request.user, wk = 3)  # changed from get to filter to avoid "Pick is not iterable" error

   return render(request, 'appmain/picks_view.html', {'picks': picks})

#TODO: add view for Teams list
#TODO: add template too (HTML) for Teams list
#TODO: add link to navbar


# form for user to pick games
#TODO: add form to display and save picks for all games for week
# @login_required
def picks_make(request):
   if not request.user.is_authenticated:
      return redirect('%s?next=%s' %(settings.LOGIN_URL, request.path))

   timezone.activate(pytz.timezone('America/Denver'))
   submitted = False

   if request.method == 'POST':
      print(f'got a response: {request.POST.get("txtPointsTotal")}')
      print(f'of Pick ID: {request.POST.get("hidPickID")}')
      pick_id = request.POST.get("hidPickID")
      pick = Pick.objects.get(pk=pick_id)
      pick.points = request.POST.get("txtPointsTotal")
      koth = Team.objects.get(id=request.POST.get("cboKingOfHillPick"))
      pick.koth_team = koth
      for i, game in enumerate(pick.pickgame_set.all(), start=1):
         print(f'Setting game for: {i} as Team: {request.POST.get("Selected"+str(i))}')
         team = Team.objects.get(id=request.POST.get("Selected"+str(i)))
         game.team = team
         game.save()
      pick.save()
      return HttpResponseRedirect('/picks/make/?submitted=True')
# TODO: change return to same page with picks displayed and "Picks Saved" response
   else:
      year = Season.objects.get(current=True)
      week_no = request.session.get('week',1)
      gt = request.session.get('gt','REG')
      try:
         wk = Week.objects.get(year=year, week_no=week_no, gt=gt)
      except:
         wk = Week.objects.get(year=year, week_no=1, gt=gt)

      pick, created = Pick.objects.get_or_create(user = request.user, wk = wk, defaults={'user': request.user, 'wk': wk, 'points': 0,'entered_by': request.user, 'updated_by': request.user})
      #TODO: add check for exception MultipleObjectsReturned  there should be only 1
      if created:
         games = Game.objects.filter(week = wk)
         for game in games:
            game_picks = PickGame.objects.create(pick_head = pick, game = game, entered_by = request.user, updated_by = request.user)
            game_picks.save()

      if 'submitted' in request.GET:
         submitted = True

      # return render(request, 'appmain/picks_make.html', {'form': form, 'submitted': submitted})
      return render(request, 'appmain/picks_make.html', {'pick': pick, 'submitted': submitted})

class PickList(ListView):
   model = Pick


class PickGameCreate(CreateView):
   model = Pick
   fields = ['user', 'wk', 'points']
   success_url = reverse_lazy('pick-list')

   def get_context_data(self, **kwargs):
      data = super(PickGameCreate, self).get_context_data(**kwargs)
      if self.request.POST:
         data['games'] = GamePickFormSet(self.request.POST)
      else:
         data['games'] = GamePickFormSet()
      return data

   def form_valid(self, form):
      context = self.get_context_data()
      games = context['games']
      with transaction.atomic():
         self.object = form.save()
         if games.is_valid():
            games.instance = self.object
            games.save()
      return super(PickGameCreate, self).from_valid(form)

