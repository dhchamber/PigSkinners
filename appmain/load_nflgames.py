import requests
from django.utils.timezone import make_aware
from datetime import datetime
import pytz
import xml.etree.ElementTree as ET
from appmain.models import Season, Week, Team, Game
import logging

logger = logging.getLogger(__name__)
# logging.config.dictConfig({
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'console': {
#             'format': '%(name)-12s %(levelname)-8s %(lineno)d %(message)s'
#         },
#         # 'file': {
#         #     'format': '%(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s'
#         # }
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'console'
#         },
#         # 'file': {
#         #     'level': 'DEBUG',
#         #     'class': 'logging.FileHandler',
#         #     'formatter': 'file',
#         #     'filename': 'debug.log'
#         # }
#     },
#     'loggers': {
#         'django.request': {
#             'level': 'DEBUG',
#             'propagate': True,
#             'handlers': ['console'],
#             # 'handlers': ['console', 'file'],
#         },
#         '': {
#             'level': 'DEBUG',
#             # 'handlers': ['console', 'file'],
#             'handlers': ['console'],
#         },
#     },
# })

# List of NFL weeks, 4 PreSeason, 17 Regular Season, and 4 Post Season
nfl_week = [(1, 'PRE'), (2, 'PRE'), (3, 'PRE'), (4, 'PRE'), (1, 'REG'), (2, 'REG'), (3, 'REG'), (4, 'REG'), (5, 'REG'),
            (6, 'REG'), (7, 'REG'), (8, 'REG'), (9, 'REG'), (10, 'REG'), (11, 'REG'), (12, 'REG'), (13, 'REG'),
            (14, 'REG'), (15, 'REG'), (16, 'REG'), (17, 'REG'), (18, 'POST'), (19, 'POST'), (20, 'POST'), (22, 'POST')]
# game_attrib_key = [(1, 'gd'), (2, 'w'), (3, 'y'), (4, 't')]  # gd?, week, year, game type P, R, P
# key = {'eid': 'eid', 'gsis': 'gsis', 'd': 'day', 't': 'time', 'q': 'status', 'h': 'home', 'hnn': 'home_nickname',
#        'htn': 'home_teamname', 'hs': 'home_score', 'v': 'visitor', 'vnn': 'visitor_nickname',
#        'vtn': 'visitor_teamname', 'vs': 'visitor_score', 'n': 'network', 'p': 'p', 'rz': 'red_zone', 'ga': 'ga',
#        'gt': 'gt'}


def load_season(season):
    for week, gt in nfl_week:
        load_score('WEEK', season, gt, week)

def load_score(url_type, year='2019', week_type='REG', week=1):
    # https://www.rubydoc.info/gems/nfl_live_update/0.0.1/NFL/LiveUpdate/ScoreStrip/Games
    if url_type == 'LIVE':
        url = 'http://www.nfl.com/liveupdate/scorestrip/ss.xml'
    elif url_type == 'POST':
        url = 'http://www.nfl.com/liveupdate/scorestrip/postseason/ss.xml'
    elif url_type == 'WEEK':
        url = 'http://www.nfl.com/ajax/scorestrip?season=' + str(year) + '&seasonType=' + week_type + '&week=' + str(
            week)
    else:
        url = None
        # print(f'Error: invalid URL type entered: {url_type}')
        logger.error(f'Error: invalid URL type entered: {url_type}')

        return

    # print(f'URL: {url}')
    logger.debug(f'URL: {url}')

    # doc has 3 sections <gms>,  <gds>, <bps>
    # gms has scores for WC, DIV, CON, PRO (Pro Bowl), SB
    # gds has score by qtr and latest down and distance
    # bps has last play for game i.e t. coleman 1 yd. TD run SF
    page = requests.get(url)
    root_xml = ET.fromstring(page.content) # root 'ss' element
    for child in root_xml:  #children are gms and possibly gds
        if child.tag == 'gms':  # add case for gds as well
            # get attributes of element
            w = y = gd = bph = bf = 0
            wk_type = ''
            for name, value in child.attrib.items():
                if name == 'bph':
                    bph = value
                elif name == 'bf':
                    bf = value
                elif name == 'gd':
                    gd = int(value)
                elif name == 't':  # P for PRE, PreSeason; R for REG, Regular Season; P or POST for PostSeason
                    wk_type = value
                elif name == 'y':  # year i.e. 2019
                    year = value
                elif name == 'w':  # week i.e. 17
                    week_no = value

            cnt = 0
            created = False
            for game_rec in child:  # 1-many g (game) records under gms tag
                cnt += 1
                created = False
                try:
                    eid = game_rec.attrib['eid']   # changed from gsis
                except:  # what should the except be?
                    # print(f'Error: eid attibute is missing')
                    logger.error('Error: eid attibute is missing from XML.  Unable to continue')
                    continue  # go to next game_rec

                try:
                    game = Game.objects.get(eid=eid)  # changed from gsis
                    created = False
                except Game.DoesNotExist:
                    if url_type in ('LIVE', 'POST'):
                        # throw error  and stop don't create  the game should have been created by load season
                        # print(f'Game not found for {eid}')
                        logger.error(f'Game not found for {eid}')
                        continue
                    elif url_type == 'WEEK':
                        # we are loading the schedule so we can create the game if needed
                        game = Game()
                        season = Season.objects.get(year=year)
                        print(f'Get Week: year: {season.year} week: {week_no} gt: {week_type}')
                        week = Week.objects.get(year=season, week_no=week_no, gt=week_type)
                        # print(f'Game created for Week #{week.week_no}')
                        logger.debug(f'Game created for Week #{week.week_no}')
                        game.week = week
                        created = True

                game.eid = eid
                game.wk_no = week_no
                game.year = year
                game.t = wk_type
                game.gd = gd
                game.bph = bph
                game.bf = bf

                # get attributes from gms record in for loop
                for name, value in game_rec.attrib.items():
                    print(f'name: {name} : value: {value}')
                    eid = gsis = home_score = visitor_score = red_zone= 0
                    gt = ga = home = visitor = home_nickname = visitor_nickname = home_teamname = visitor_teamname = ''
                    if name == 'gsis':      # GSIS (Game Statistics and Information System)
                        game.gsis = value
                    elif name == 'gt':
                        game.gt = value
                    elif name == 'h':
                        home = value
                        game.home = value
                        # if home == 'LA':
                        #     home = 'LAR'
                        try:
                            game.home_team = Team.objects.get(team_abrev=home)
                        except Team.DoesNotExist:
                            team = Team(team_abrev=home, short_name=home, team_name=home)
                            team.save()
                            game.home_team = team
                    elif name == 'hnn':
                        game.home_nickname = value
                    elif name == 'htn':
                        game.home_teamname = value
                    elif name == 'hs':
                        game.home_score = int(value)
                    elif name == 'v':
                        visitor = value
                        game.visitor = value
                        # if visitor == 'LA':
                        #     visitor = 'LAR'
                        try:
                            game.visitor_team = Team.objects.get(team_abrev=visitor)
                        except Team.DoesNotExist:
                            team = Team(team_abrev=visitor, short_name=visitor, team_name=visitor)
                            team.save()
                            game.visitor_team = team
                    elif name == 'vnn':
                        game.visitor_nickname = value
                    elif name == 'vtn':
                        game.visitor_teamname = value
                    elif name == 'vs':
                        game.visitor_score = int(value)
                    elif name == 'rz':
                        game.red_zone = value
                    elif name == 'ga':
                        game.ga = value
                    elif name == 't':
                        game.time = value
                    elif name == 'q':
                        game.status = value
                    elif name == 'd':
                        game.day = value
                    elif name == 'p':
                        game.p = value
                    elif name == 'k':
                        game.k = value
                    elif name == 'n':
                        game.network = value
                # end of for name, value in game_rec.attrib.items():
                # calculate datetime field of game from eid and time

                print(f'game EID: {game.eid}')
                date_yr = int(game.eid[:4])
                mo = int(game.eid[4:6])
                day = int(game.eid[6:8])
                hour, minute = game.time.split(':')
                if int(hour) < 12:
                    hour = int(hour) + 12
                else:
                    hour = int(hour)
                dt = str(date_yr) + '-' + str(mo) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute)
                dt2 = datetime.strptime(dt,'%Y-%m-%d %H:%M')
                game.date_time = make_aware(datetime(date_yr, mo, day, hour, int(minute)), pytz.timezone('America/New_York'))

                game.save()

                if game.home_nickname is not None and game.home_nickname != '':
                    game.home_team.short_name = game.home_nickname.capitalize()

                if game.home_teamname is not None and game.home_teamname != '':
                    game.home_team.team_name = game.home_teamname.capitalize()

                if game.visitor_nickname is not None and game.visitor_nickname != '':
                    game.visitor_team.short_name = game.visitor_nickname.capitalize()

                if game.visitor_teamname is not None and game.visitor_teamname != '':
                    game.visitor_team.team_name = game.visitor_teamname.capitalize()

                game.set_winner()
                game.update_score()
                # print(f'Game #{cnt} {game.id} loaded for Week {game.wk_no} year {game.year} Winner: {game.winner} ')
                logger.debug(f'Game #{cnt} {game.id} loaded for Week {game.wk_no} year {game.year} Winner: {game.winner}')
            # end of for game_rec in ss:

            # set points game for the last game in the list if this is a regular or pre season game and just created
            if game.week.gt in ('PRE', 'REG') and created == True:
                game.points_game = True
                print(f'Points Game set {game.gsis} {game.eid} Week/Yr {game.week}/{game.year} Winner: {game.winner}')
                logger.debug(f'Points Game set {game.gsis} {game.eid} Week/Yr {game.week}/{game.year} Winner: {game.winner}')
                game.save()

        # elif child.tag == 'gds':  add else if for gds which has more live score data, dad = down and distance
        #             attributes: gsis, eid, vtol, htol, vot, v4q, v3q, v2q, v1q, hot, h4q, h3q, h2q, h1q,

        # elif child.tag == 'bps':  add else if for bps which has more dad = down and distance and last play
