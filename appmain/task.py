from background_task import background
from django.contrib.auth.models import User
from appmain.load_nflgames import load_score
from appmain.models import Season


@background(schedule=60)
def load_scores(url_type, repeat=60):
    load_score(url_type='LIVE')


@background(schedule=600)
def close_curr_week():
    year = Season.objects.get(current=True)
    week = year.current_week()
    user = User.objects.get(id=1)
    print(f'Close week: {week.week_no}')
    week.close_week(user)
