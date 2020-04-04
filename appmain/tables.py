import django_tables2 as tables
from .models import Team, Season, Game, PickGame

# tutorial/tables.py
class GameTable(tables.Table):
   class Meta:
      model = Game
      template_name = "django_tables2/bootstrap.html"
      fields = ("week_id","wk_no","gt","gsis","date_time","status","home","home_score","visitor","visitor_score","p","red_zone")


class TeamTable(tables.Table):
   class Meta:
      model = Season
      template_name = "django_tables2/bootstrap.html"
      fields = ("team_abrev", "short_name","team_name","division","city_name")

class SeasonTable(tables.Table):
   class Meta:
      model = Season
      template_name = "django_tables2/bootstrap.html"
      fields = ("year", "current","start_date","end_date")

class PickGameTable(tables.Table):
   class Meta:
      model = PickGame
      template_name = "django_tables2/bootstrap.html"
      fields = ("parent.wk.week_no", "game.visitor_team.team_name","game.home_team.team_name", "team.team_abrev", "status", "entered_by")

