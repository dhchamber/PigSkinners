import requests
from django.utils.timezone import make_aware
from datetime import datetime
import pytz
import xml.etree.ElementTree as ET
from appmain.models import Season, Week, Team, Game
from django.core.exceptions import ObjectDoesNotExist

# List of NFL weeks, 4 PreSeason, 17 Regular Season, and 4 Post Season
nfl_week = [(1,'PRE'), (2,'PRE'), (3,'PRE'), (4,'PRE'), (1,'REG'), (2,'REG'), (3,'REG'), (4,'REG'), (5,'REG'), (6,'REG'), (7,'REG'), (8,'REG'), (9,'REG'), (10,'REG'), (11,'REG'), (12,'REG'), (13,'REG'), (14,'REG'), (15,'REG'), (16,'REG'), (17,'REG'), (18,'POST'), (19,'POST'), (20,'POST'), (22,'POST')]
game_attrib_key = [(1,'gd'), (2,'w'), (3,'y'), (4,'t')]  # gd?, week, year, game type P, R, P


def LoadWeek():
   for season in Season.objects.all():
      yr = season.yr
      print(f'Loading weeks for {yr} ')
      for week, gt in nfl_week:
         print(f'Begin loading week {week} {gt} ')
         week, created = Week.objects.get_or_create(year = season, week_no = week, gt = gt)
         week.save()
         print(f'Week # {week} {gt} loaded ')

def live_scores_reg():
   # url = 'http://www.nfl.com/liveupdate/scorestrip/ss.xml'
   url = 'http://www.nfl.com/liveupdate/scorestrip/postseason/ss.xml'
   page = requests.get(url)
   page_xml = ET.fromstring(page.content)

   for gms in page_xml:
      # for key, attr in game_attrib_key:
      if gms.tag == 'gms':
         cnt = 0
         for score in gms:
            cnt += 1
            try:
               sch_game = Game.objects.get(gsis=score.attrib['gsis'])
            except ObjectDoesNotExist:
               # throw error  and stop don't create
               continue

            #    print(f'gms: {gms} ')
            # sch_game.gd = gms.attrib['gd']
            sch_game.wk_no = gms.attrib['w']
            sch_game.year = gms.attrib['y']
            sch_game.t = gms.attrib['t']
            sch_game.bph = gms.attrib['bph']
            # shouldn't need to update week, so leave this out
            y  = gms.attrib['y']
            w = gms.attrib['w']
            # week = Week.objects.get(year=y, week_no=gms.attrib['w'], gt=gt)
            # print(f'Week #{week.week_no} ')
            # sch_game.week = week

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
                  sch_game.home_nickname = score.attrib[k]
               elif k == 'htn':
                  sch_game.home_teamname = score.attrib[k]
               elif k == 'hs':
                  if score.attrib[k].isnumeric():
                     sch_game.home_score = score.attrib[k]
               elif k == 'v':
                  sch_game.visitor = score.attrib[k]
               elif k == 'vnn':
                  sch_game.visitor_nickname = score.attrib[k]
               elif k == 'vtn':
                  sch_game.visitor_teamname = score.attrib[k]
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
            # End of for k in score.attrib.keys():
            sch_game.save()
            print(f'LiveGame #{cnt} {sch_game.gsis}loaded for Week {w} for year {y}')
         else:
            continue
         # End of for score in gms:

      print(f'Week # {w} loaded for year {y}')
      # End of for gms in page_xml:


def LoadSeason(season):
   yr = season
   # game_first = -4 # start at -4 to get PreSeason games
   # game_last = 22  # 22 is SB
   for week, gt in nfl_week:
      # get games and convert to XML
      url = 'http://www.nfl.com/ajax/scorestrip?season=' + yr + '&seasonType=' + gt + '&week=' + str(week)
      page = requests.get(url)
      print(f'Page URL: {url}')
      page_xml = ET.fromstring(page.content)

      for gms in page_xml:
         cnt = 0
         for score in gms:
            cnt += 1
            try:
               sch_game = Game.objects.get(gsis=score.attrib['gsis'])
            except ObjectDoesNotExist:
               sch_game = Game()
               sch_game.gd = gms.attrib['gd']
               sch_game.wk_no = gms.attrib['w']
               sch_game.year = gms.attrib['y']
               sch_game.t = gms.attrib['t']
               y = Season.objects.get(yr = yr)
               week = Week.objects.get(year = y, week_no = gms.attrib['w'], gt = gt)
               print(f'Week #{week.week_no} ')
               sch_game.week = week

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
                  if score.attrib[k] == 'LA':
                     team = 'LAR'
                  else:
                     team = score.attrib[k]
                  sch_game.home_team = Team.objects.get(team_abrev = team)
               elif k == 'hnn':
                  sch_game.home_name = score.attrib[k]
               elif k == 'hs':
                  if score.attrib[k].isnumeric():
                     sch_game.home_score = score.attrib[k]
               elif k == 'v':
                  sch_game.visitor = score.attrib[k]
                  if score.attrib[k] == 'LA':
                     team = 'LAR'
                  else:
                     team = score.attrib[k]
                  sch_game.visitor_team = Team.objects.get(team_abrev = team)
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
            #End of for k in score.attrib.keys():
            sch_game.save()
            # calculate datetime field of game from eid and time
            year = int(sch_game.eid[:4])
            mo = int(sch_game.eid[4:6])
            day = int(sch_game.eid[6:8])
            hour, min = sch_game.time.split(':')
            if int(hour) < 12:
               h = int(hour) + 12
            else:
               h = int(hour)
            sch_game.date_time = make_aware(datetime(year, mo, day, h, int(min)), pytz.timezone('America/New_York'))
            sch_game.save()
            print(f'Game #{cnt} loaded for Week {week} for year {year} ')
         #End of for score in gms:
         print(f'Week # {week} loaded for year {year}')
      #End of for gms in page_xml:
   #End of for i in range(game_first, game_last+1):
#End of function

def LoadScores(season_type):
   if season_type == 'REG':
      # doc has 1 section <gms>
      url = 'http://http://www.nfl.com/liveupdate/scorestrip/ss.xml'
   elif season_type == 'POST':
      # doc has 3 sections <gms>,  <gds>, <bps>
      # gms has scores for WC, DIV, CON, PRO (Pro Bowl), SB
      # gds has score by qtr and latest down and distance
      # bps has last play for game i.e t. coleman 1 yd. TD run SF
      url = 'http: // www.nfl.com / liveupdate / scorestrip / postseason / ss.xml'
   else:
      url = ''

   # get current game scores and convert to XML
   page = requests.get(url)
   page_xml = ET.fromstring(page.content)  # doc has 3 sect

   for gms in page_xml:  # there is only 1
      w = gms.attrib['w']  # week i.e. 17
      y = gms.attrib['y']  # year i.e. 2019
      t = gms.attrib['t']  # P for PRE, PreSeason; R for REG, Regular Season; P for POST, PostSeason
      gd = gms.attrib['gd'] #?? i.e. 1
      bf = gms.attrib['bf'] #?? i.e. 1
      bph = gms.attrib['bph'] #?? i.e. 172

      cnt = 0
      for score in gms:
         cnt += 1
         try:
            sch_game = Game.objects.get(gsis=score.attrib['gsis'])
         except ObjectDoesNotExist:
            # shouldn't have to add new game here.  should this be an error?
            sch_game = Game()
            sch_game.gd = gd
            sch_game.wk_no = w
            sch_game.year = y
            sch_game.t = t
            # week = Week.objects.get(year_id = year, week_no = w)
            # print(f'Week #{w}  year {year}  WeekObj {week.year}')
            # sch_game.week = week

         for k in score.attrib.keys():
            # don't update eid or gsis
            # if k == 'eid' and sch_game.eid == '':
            #       sch_game.eid = score.attrib[k]
            # elif k == 'gsis' and sch_game.gsis == '':
            #    sch_game.gsis = score.attrib[k]
            if k == 'd':
               sch_game.day = score.attrib[k]
            elif k == 't':
               sch_game.time = score.attrib[k]
            elif k == 'q':
               sch_game.status = score.attrib[k]
            elif k == 'k':
               sch_game.k = score.attrib[k]
            elif k == 'h':    # scoreboard name "HOU"
               sch_game.home = score.attrib[k]
            elif k == 'htn': # home team name "Houston Texans"
               sch_game.home_name = score.attrib[k]
            elif k == 'hnn': # nickname  "texans"
               sch_game.home_name = score.attrib[k]
            elif k == 'hs':
               if score.attrib[k].isnumeric():
                  sch_game.home_score = score.attrib[k]
            elif k == 'v':
               sch_game.visitor = score.attrib[k]
            elif k == 'vtn':
               sch_game.visitor_name = score.attrib[k]
            elif k == 'vnn':
               sch_game.visitor_name = score.attrib[k]
            elif k == 'vs':
               if score.attrib[k].isnumeric():
                  sch_game.visitor_score = score.attrib[k]
            elif k == 'N':    # network   ESPN
               sch_game.network = score.attrib[k]
            elif k == 'p':
               sch_game.p = score.attrib[k]
            elif k == 'rz':
               sch_game.red_zone = score.attrib[k]
            elif k == 'ga':
               sch_game.ga = score.attrib[k]
            elif k == 'gt':   # game type  WC
               sch_game.gt = score.attrib[k]
   #      else:
   #            print(f"something: {score.attrib[k]}")
         #End of for k in score.attrib.keys():
         sch_game.save()
         print(f'Game #{cnt} loaded for Week {i} ')
      #End of for score in gms:
      print(f'Week # {i} loaded ')
      #End of for gms in page_xml:
#End of function