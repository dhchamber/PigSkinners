from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

# from django.contrib import admin
# from django.contrib.auth import views as auth_views
# from appmain.views import game_list, PickListView, GameListView, TeamListView


urlpatterns = [
    path('ps_home/', views.home, name='ps_home'),
    path('login', auth_views.LoginView.as_view(), name='login'),
    # path('signin', auth_views.LoginView.as_view(), name='signin'),
    path('password/change', views.change_password, name='change_password'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # had to add this to get the last step of password reset to work
    # path('accounts/reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path(r'reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
    #     auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('user/profile/', views.user_profile, name='profile'),
    path('pick/view/', views.pick_view, name='pick_view'),
    path('pick/make/', views.pick_make, name='pick_make'),
    path('pick/make_ps/', views.pick_make_ps, name='pick_make_ps'),
    # path('pick/save_ps/', views.pick_save_ps, name='pick_save_ps'),
    path('pick/revision/', views.pick_revision, name='pick_revision'),
    path('standing/weeksum/', views.standing_weeksum, name='standing_weeksum'),
    path('standing/weekdet/', views.standing_weekdet, name='standing_weekdet'),
    path('standing/weekpros/', views.standing_week_prospective, name='standing_weekpros'),
    path('standing/season/', views.standing_season, name='standing_season'),
    path('standing/koth/', views.standing_koth, name='standing_koth'),
    path('standing/post/', views.standing_post, name='standing_post'),
    path('setup/teams/', views.teams_view, name='setup_teams'),
    path('setup/weeks/', views.setup_weeks, name='setup_weeks'),
    path('setup/games/', views.games_view, name='setup_games'),
    path('setup/season/', views.SeasonListView.as_view(), name='setup_season'),
    path('action/week/', views.action_week, name='action_week'),
    path('action/random/', views.random_picks, name='random_picks'),
    # path('setup/seasonweek/<int:pk>/', views.SeasonUpdate.as_view(), name='season-list'),
    # path('season/add/', views.SeasonWeekCreate.as_view(), name='season-add'),
    # path('season/update/<int:pk>', views.SeasonWeekUpdate.as_view(), name='season-update'),
    # path('season/delete/<int:pk>', views.SeasonDelete.as_view(), name='season-delete'),

    path('user_list/', views.user_list, name='user_list'),
    path('', views.home, name='home'),
]

    # path('setup/game2/', GameListView.as_view(), name='setup_game2'),
    # path('setup/game2/', game_list, name='setup_game2'),
    # path('setup/teams/', TeamListView.as_view(), name='setup_teams'),
    # path('picks/view/', views.PickListView.as_view(), name='picks_view'),
    # path('add_pick/', views.add_pick, name='add-pick'),  # \myclub_root\events\urls.py

