# from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from appmain.views import game_list, GameListView, TeamListView  #PickListView
from . import views


urlpatterns = [
    path('ps_home/', views.home, name='ps_home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('password/change', views.change_password, name='change_password'),
    path('pick/view/', views.pick_view, name='pick_view'),
    # path('picks/view/', views.PickListView.as_view(), name='picks_view'),
    path('pick/make/', views.pick_make, name='pick_make'),
    path('pick/make_ps/', views.pick_make_ps, name='pick_make_ps'),
    path('pick/save_ps/', views.pick_save_ps, name='pick_save_ps'),
    path('pick/revision/', views.pick_revision, name='pick_revision'),
    path('standing/weeksum/', views.standing_weeksum, name='standing_weeksum'),
    path('standing/weekdet/', views.standing_weekdet, name='standing_weekdet'),
    path('standing/weekpros/', views.standing_week_prospective, name='standing_weekpros'),
    path('standing/season/', views.standing_season, name='standing_season'),
    path('standing/koth/', views.standing_koth, name='standing_koth'),
    path('standing/post/', views.standing_post, name='standing_post'),
    path('setup/teams/', views.teams_view, name='setup_teams'),
    path('setup/weeks/', views.setup_weeks, name='setup_weeks'),
    # path('setup/teams/', TeamListView.as_view(), name='setup_teams'),
    path('setup/games/', views.games_view, name='setup_games'),
    path('setup/game2/', GameListView.as_view(), name='setup_game2'),
    # path('setup/game2/', game_list, name='setup_game2'),
    path('action/week/', views.action_week, name='action_week'),
    path('action/random/', views.random_picks, name='random_picks'),

    # path('add_pick/', views.add_pick, name='add-pick'),  # \myclub_root\events\urls.py
    path('', views.home, name='home'),
]
