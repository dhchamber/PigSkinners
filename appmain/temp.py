import requests
import xml.etree.ElementTree as ET
# added per web to run script outside of Django website.  not sure why
import os
import django
from django.core.exceptions import ObjectDoesNotExist

os.environ['DJANGO_SETTINGS_MODULE'] = 'PigSkinners.settings'
django.setup()

from appmain.models import NflGame

year = '2019'
season_type = 'POST'  # REG
game_first = 18 #1
game_last = 19 #17

games = NflGame.objects.filter(wk=1).order_by('gsis')

for i in range(game_first, game_last+1):
   page = requests.get('http://www.nfl.com/ajax/scorestrip?season=' + year + '&seasonType=' + season_type + '&week=' + str(i))
   page_xml = ET.fromstring(page.content)

   for gms in page_xml:
      for score in gms:
         try:
            sch_game = NflGame.objects.get(gsis=score.attrib['gsis'])
         except ObjectDoesNotExist:
            sch_game = NflGame()

         for k in score.attrib.keys():
            if k == 'eid' and sch_game.eid == '':
                  sch_game.eid = score.attrib[k]
            elif k == 'gsis' and sch_game.gsis == '':
               sch_game.gsis = score.attrib[k]
            elif k == 'd':
               sch_game.day = score.attrib[k]
            elif k == 't':
               sch_game.time = score.attrib[k]
            elif k == 'q':
               sch_game.status = score.attrib[k]
            elif k == 'k':
               sch_game.k = score.attrib[k]
            elif k == 'h':
               sch_game.home = score.attrib[k]
            elif k == 'hnn':
               sch_game.home_name = score.attrib[k]
            elif k == 'hs':
               if score.attrib[k].isnumeric():
                  sch_game.home_score = score.attrib[k]
            elif k == 'v':
               sch_game.visitor = score.attrib[k]
            elif k == 'vnn':
               sch_game.visitor_name = score.attrib[k]
            elif k == 'vs':
               if score.attrib[k].isnumeric():
                  sch_game.visitor_score = score.attrib[k]
            elif k == 'p':
               sch_game.p = score.attrib[k]
            elif k == 'rz':
               sch_game.red_zone = score.attrib[k]
            elif k == 'ga':
               sch_game.ga = score.attrib[k]
            elif k == 'gt':
               sch_game.gt = score.attrib[k]
   #      else:
   #            print(f"something: {score.attrib[k]}")
         sch_game.save()
         print(f'Game # loaded for Week {i} for year {year}')
      print(f'Week # {i} loaded for year {year}')

