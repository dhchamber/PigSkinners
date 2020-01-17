import django_tables2 as tables
from .models import Team, Game


# tutorial/tables.py
class GameTable(tables.Table):
   class Meta:
      model = Game
      template_name = "django_tables2/bootstrap.html"
      fields = ("wk_no","gsis","home","home_score","visitor","visitor_score","p","red_zone","gt")


class TeamTable(tables.Table):
   class Meta:
      model = Team
      template_name = "django_tables2/bootstrap.html"
      fields = ("team_abrev", "short_name","team_name","division","city_name")
