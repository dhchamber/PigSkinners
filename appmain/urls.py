# from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from appmain.views import game_list, GameListView, TeamListView
from . import Picks
from . import views


urlpatterns = [
    path('ps_home/', views.home, name='ps_home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('picks/view/', views.picks_view, name='picks_view'),
    path('picks/make/', views.picks_make, name='picks_make'),
    path('picks/revisions/', views.picks_revisions, name='picks_revisions'),
    path('standing/weekdet/', views.standing_weekdet, name='standing_weekdet'),
    path('standing/season/', views.standing_season, name='standing_weeksum'),
    path('standing/koth/', views.standing_koth, name='standing_koth'),
    path('setup/teams/', views.teams_view, name='setup_teams'),
    path('setup/weeks/', views.setup_weeks, name='setup_weeks'),
    # path('setup/teams/', TeamListView.as_view(), name='setup_teams'),
    path('setup/games/', views.games_view, name='setup_games'),
    path('setup/game2/', GameListView.as_view(), name='setup_game2'),
    # path('setup/game2/', game_list, name='setup_game2'),
    # path('picks/form/', Picks.contact, name = 'picks'),  # myclub_root\myclub_site\urls.py
    # path('picks/new/', PickGameCreate.as_view(), name='games_new'),
    path('action/week/', views.action_week, name='action_week'),
    path('action/random/', views.random_picks, name='random_picks'),

    # path('add_pick/', views.add_pick, name='add-pick'),  # \myclub_root\events\urls.py
    path('', views.home, name='home'),
]
