from django.contrib import admin
from .models import Season, Week,Team, Game, Seed, PostPoint , PostSeason


class SeasonAdmin(admin.ModelAdmin):
    list_display = ('year', 'current', 'start_date', 'end_date')


class SeedAdmin(admin.ModelAdmin):
    list_display = ('year', 'team', 'seed')


class PostSeasonAdmin(admin.ModelAdmin):
    list_display = ('year', 'AWC45', 'NWC45', 'AWC36', 'NWC36', 'ADIV1', 'NDIV1', 'ADIV2', 'NDIV2', 'ACONF', 'NCONF', 'SB')


class PostPointAdmin(admin.ModelAdmin):
    list_display = ('gt', 'points')


class WeekAdmin(admin.ModelAdmin):
    list_display = ('id', 'year', 'week_no', 'gt', 'start_date', 'end_date', 'closed', 'forecast_date_closed')


class GameAdmin(admin.ModelAdmin):
    list_display = ('eid', 'gsis', 'gt', 'wk_no', 'day', 'time', 'status', 'home', 'home_score', 'visitor', 'visitor_score','points_game')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'team_abrev', 'short_name', 'team_name', 'conference', 'division', 'city_name')

admin.site.register(Season, SeasonAdmin)
admin.site.register(Seed, SeedAdmin)
admin.site.register(PostSeason, PostSeasonAdmin)
admin.site.register(PostPoint, PostPointAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Game, GameAdmin)

