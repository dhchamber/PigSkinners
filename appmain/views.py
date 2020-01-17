from django.shortcuts import render, redirect  # add redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate  # new
# from django.contrib.auth.forms import UserCreationForm  # new
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from appmain.forms import SignUpForm, PickForm  # add PickForm
from django_tables2 import SingleTableView # django-tables2 readthedocs.io

from .models import Season, Week, Pick, Team, Game
from appmain.load_nflgames import LoadWeek, LoadSeason, live_scores_reg
from .tables import TeamTable, GameTable  # tutorial page 2 - QuerySets [implied] + django-tables2 readthedocs.io

# tutorial page 1
class GameListView(ListView):
   model = Game
   template_name = 'appmain/game.html'

   def get_queryset(self):
      week = Week.objects.get(week_no=15)
      return Game.objects.filter(week=week)  # week 17 games

# django-tables2 readthedocs.io
class TeamListView(SingleTableView):
   model = Team
   table_class = TeamTable
   template_name = 'appmain/team.html'


# tutorial/views.py
# class GameListView(SingleTableView):
#    model = Game
#    table_class = GameTable
#    template_name = 'appmain/game.html'

# tutorial page 2 - QuerySets
# takes table GameTable based on model Game
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


def games_view(request):
   # if request.method == 'POST' and 'load_games' in request.POST:
   #    load_games()
   #    #return user to page
   #    return HttpResponseRedirect(reverse(games_view()))
   # else:
   year = Season.objects.get(current=True)
   week = Week.objects.get(year=year, week_no= 1, gt='REG')
   print(f'Found Week # {week.week_no} loaded for year {year.yr}')
   games = Game.objects.filter(week=week)
   print(f'Found games # {games.count()} ')
   return render(request, 'appmain/games_view.html', {'games': games})
#       return render(request, 'appmain/new_games.html', {'games': games})


# new signup form
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

# Create your views here.
def update_profile(request, user_id):
   user = User.objects.get(pk=user_id)
   user.profile.bio = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit...'
   user.save()

def post_list(request):
    return render(request, 'appmain/post_list.html', {})

#def home_frame(request):
#    return render(request, 'appmain/home_frame.html', {})


def home(request):
   weeks = Week.objects.filter(id=1)
   return render(request, 'appmain/home.html', {'weeks': weeks})


def picks_view(request):
   games = Game.objects.filter(wk_id=1).order_by('gsis')
   return render(request, 'appmain/picks_view.html', {'games': games})


def picks_make(request):
    return render(request, 'appmain/picks_make.html', {})


def picks_revisions(request):
    return render(request, 'appmain/picks_revisions.html', {})


def teams_view(request):
   teams = Team.objects.all()
   return render(request, 'appmain/teams_view.html', {'teams': teams})



def picks_view(request):
   # try:
   picks = Pick.objects.filter(user = request.user, wk = 3)  # changed from get to filter to avoid "Pick is not iterable" error
   # except Pick.DoesNotExist:
   if picks.count() == 0:
      pick_wk = Pick()
      pick_wk.user = request.user
      pick_wk.wk = Week.objects.filter(year=2018,week=3)
      pick_wk.points = 41
      pick_wk.entered_by = request.user
      pick_wk.updated_by = request.user
      pick_wk.save()
      pick_wk = Pick.objects.filter(user = request.user, wk = 3)  # changed from get to filter to avoid "Pick is not iterable" error

   return render(request, 'appmain/picks_view.html', {'picks': picks})

#TODO: add view for Teams list
#TODO: add template too (HTML) for Teams list
#TODO: add link to navbar

# \myclub_root\events\views.py
def add_pick(request):
    submitted = False
    if request.method == 'POST':
        form = PickForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_pick/?submitted=True')
    else:
        form = PickForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'appmain/add_pick.html', {'form': form, 'submitted': submitted})
