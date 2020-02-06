import requests
from django.utils.timezone import make_aware
from datetime import datetime
import pytz
import xml.etree.ElementTree as ET
from appmain.models import Season, Week, Team, Game
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

# List of NFL weeks, 4 PreSeason, 17 Regular Season, and 4 Post Season
nfl_week = [(1,'PRE'), (2,'PRE'), (3,'PRE'), (4,'PRE'), (1,'REG'), (2,'REG'), (3,'REG'), (4,'REG'), (5,'REG'), (6,'REG'), (7,'REG'), (8,'REG'), (9,'REG'), (10,'REG'), (11,'REG'), (12,'REG'), (13,'REG'), (14,'REG'), (15,'REG'), (16,'REG'), (17,'REG'), (18,'POST'), (19,'POST'), (20,'POST'), (22,'POST')]
game_attrib_key = [(1,'gd'), (2,'w'), (3,'y'), (4,'t')]  # gd?, week, year, game type P, R, P
key = {'eid': 'eid', 'gsis': 'gsis', 'd': 'day', 't': 'time', 'q': 'status', 'h': 'home', 'hnn': 'home_nickname', 'htn': 'home_teamname', 'hs': 'home_score', 'v': 'visitor', 'vnn': 'visitor_nickname',
       'vtn': 'visitor_teamname', 'vs': 'visitor_score', 'n': 'network', 'p': 'p', 'rz': 'red_zone', 'ga': 'ga', 'gt': 'gt'}


def load_week():
   # load week objects for a new year.  add this as a method when adding a new year?
   for season in Season.objects.all():
      yr = season.year
      print(f'Loading weeks for {yr} ')
      for week, gt in nfl_week:
         week, created = Week.objects.get_or_create(year=season, week_no=week, gt=gt)
         week.save()
         print(f'Week # {week} {gt} loaded ')


def update_score(g):
   pgames = g.pick_game.all()
   for pg in pgames:
      if pg.team != None:
         if g.status == 'P':
            if pg.team == g.winner:
               pg.status = 'w'
            elif g.home_score == g.visitor_score:
               pg.status = 't'
            else:
               pg.status = 'l'
         else:
            if pg.team == g.winner:
               pg.status = 'W'
            elif g.home_score == g.visitor_score:
               pg.status = 'T'
            else:
               pg.status = 'L'
         pg.save()


def set_winner(g):
   # set game winner
   if g.status[:1] == 'F':
      if g.home_score > g.visitor_score:
         g.winner = g.home_team
      elif g.home_score < g.visitor_score:
         g.winner = g.visitor_team
      else:
         g.winner = None
   g.save()


def load_score(season_type):
   if season_type == 'REG':
      url = 'http://www.nfl.com/liveupdate/scorestrip/ss.xml'
   elif season_type == 'POST':
      url = 'http://www.nfl.com/liveupdate/scorestrip/postseason/ss.xml'
   else:
      url = None
   # elif type == 'season':
   #    yr = '2019'
   #    gt = 'REG'
   #    week = '01'
   #    url = 'http://www.nfl.com/ajax/scorestrip?season=' + yr + '&seasonType=' + gt + '&week=' + str(week)

   # doc has 3 sections <gms>,  <gds>, <bps>
   # gms has scores for WC, DIV, CON, PRO (Pro Bowl), SB
   # gds has score by qtr and latest down and distance
   # bps has last play for game i.e t. coleman 1 yd. TD run SF
   page = requests.get(url)
   page_xml = ET.fromstring(page.content)
   for ss in page_xml:
      if ss.tag == 'gms':  # add case for gds as well
         cnt = 0
         for game_rec in ss:
            cnt += 1
            # get existing game record
            print(f'Game_rec: {game_rec} ')
            try:
               g = Game.objects.get(eid=game_rec.attrib['eid']) # changed from gsis
               print(f'Found game {g.id} for gsis code {game_rec.attrib["eid"]}')
            except ObjectDoesNotExist:
               # throw error  and stop don't create
               print(f'Game not found for {game_rec.attrib["eid"]}')
               continue

            try:
               g.gd = int(ss.attrib['gd'])
            except KeyError:
               print(f'xml rec has no attribute "gd" ')
            g.wk_no = ss.attrib['w']  # week i.e. 17
            g.year = ss.attrib['y']   # year i.e. 2019
            g.t = ss.attrib['t']      # P for PRE, PreSeason; R for REG, Regular Season; P for POST, PostSeason
            g.bph = ss.attrib['bph']
            y = ss.attrib['y']
            w = ss.attrib['w']

            for k, val in key.items():
               try:
                  if k in ('hs', 'vs'):
                     int_val = int(game_rec.attrib[k])
                     setattr(g, val, int_val)
                     print(f' and {game_rec.attrib[k]} ')
                  elif k in ('htn','vtn', 'n') and type == 'reg_live':
                     print(f'Skipping {val} for {type}')
                  else:
                     setattr(g, val, game_rec.attrib[k])
                     print(f' and {game_rec.attrib[k]} ')
               except KeyError:
                  print(f'Key error on key {k} / {val}')
            g.save()

            set_winner(g)
            update_score(g)
            print(f'Game #{cnt} {g.id} loaded for Week {g.wk_no} for year {g.year} Winner: {g.winner} ')


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
               sch_game = Game.objects.get(eid=score.attrib['eid'])
            except ObjectDoesNotExist:
               sch_game = Game()
               sch_game.gd = gms.attrib['gd']
               sch_game.wk_no = gms.attrib['w']
               sch_game.year = gms.attrib['y']
               sch_game.t = gms.attrib['t']
               y = Season.objects.get(year = yr)
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

            # set game winner
            # update pick scores for picks
            set_winner(sch_game)
            update_score(sch_game)
            print(f'Game #{cnt} {sch_game.id} loaded for Week {week} for year {year} Winner: {sch_game.winner} ')

         #End of for score in gms:
         print(f'Week # {week} loaded for year {year}')
      #End of for gms in page_xml:
   #End of for i in range(game_first, game_last+1):
#End of function