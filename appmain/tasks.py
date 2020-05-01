from celery import task, shared_task
from background_task import background
from django.contrib.auth.models import User
from appmain.load_nflgames import load_score
from appmain.models import Season
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# @background(schedule=60)    # this decorator is for background-tasks app
# def load_scores(url_type, repeat=60):
@task
def load_scores(url_type):
    load_score(url_type='LIVE')


# @background(schedule=600)   # this decorator is for background-tasks app
@shared_task
def close_curr_week():
    year = Season.objects.get(current=True)
    logger.info(f'TASK: Close week for : {year.year}')
    week = year.current_week()
    logger.info(f'TASK: Close week for week: {week.start_dt()} at time {timezone.now()} forecast {week.forecast_dt_closed()}')
    user = User.objects.get(id=1)
    logger.info(f'TASK: Close week by: {user.last_name}')
    close = week.close_week(user)
    print(f'Close week has been run: {close}')
    return close

