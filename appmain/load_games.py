import requests
import datetime
import xml.etree.ElementTree as ET
# added per web to run script outside of Django website.  not sure why
# import sys
import os
import django
from appmain.models import Game,Team, NflGame

#sys.path.append('/home/skallars/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'PigSkinners.settings'
django.setup()


page = requests.get('http://www.nfl.com/ajax/scorestrip?season=2019&seasonType=REG&week=1')
page_xml = ET.fromstring(page.content)

for gms in page_xml:
   for score in gms:
      sch_game = Game()
      sch_game.Year_id = 2019
      for k in score.attrib.keys():
         if k == 'eid':
            year = score.attrib[k][:4]
            mo = score.attrib[k][5:6]
            day = score.attrib[k][7:8]
            date_str = year + '-' + mo + '-' + day
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            sch_game.game_number = score.attrib[k][9:]
            sch_game.game_date = date_obj
         elif k == 'h':
            team = Team.objects.filter(team_abrev=score.attrib[k])
            sch_game.home_team_id = team[0].id
#      else:
#            print(f"something: {score.attrib[k]}")
         sch_game.save()

