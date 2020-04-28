import pytest

from appmain.models import Season, Week, PickGame, Game

@pytest.mark.django_db
def test_pick_game():
    year = Season.objects.get(current=True)
    weeks = Week.objects.filter(year=year, gt='REG')
    pickgames = PickGame.objects.filter(pick_head__wk__in=weeks, pick_head__saved=True)
    for pg in pickgames:
        assert pg.team in (pg.game.home_team, pg.game.visitor_team)
        # assert pg.status == pg.game.status

