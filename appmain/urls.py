from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('ps_home/', views.home, name='ps_home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('picks/view/', views.picks_view, name='picks_view'),
    path('picks/make/', views.picks_make, name='picks_make'),
    path('picks/revisions/', views.picks_revisions, name='picks_revisions'),
    path('', views.home, name='home'),
]
