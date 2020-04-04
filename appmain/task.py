from background_task import background
from django.contrib.auth.models import User
from appmain.load_nflgames import load_score

@background(schedule=60)
def load_scores(url_type, repeat=60):
    load_score(url_type='LIVE')