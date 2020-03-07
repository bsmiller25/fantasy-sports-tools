# keeper_eligble.py
import os
import pandas as pd
import espn_api.baseball as ball
import pickle
from dotenv import load_dotenv
load_dotenv()
import pdb


def is_eligible(player):
    NL = ['FA',
          'ATL', 'WAS', 'NYM', 'PHL', 'MIA',
          'CIN', 'STL', 'CHC', 'MIL', 'PIT',
          'SF', 'SD', 'ARI', 'COL', 'LAD'
          ]

    if player.proTeam in NL and player.acquisitionType == 'DRAFT':
        return(True)
    else:
        return(False)

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))
          
    

def keeper_eligible():
    """find players who are keeper eligible"""

    # connect to the league via espn api
    try:
        fileObj = open('cookies.pkl', 'rb')
        cookies = pickle.load(fileObj)
    except:
        cookies = False

    if cookies:
        try:
            league = ball.League(os.environ.get('BALL_ID'), 2020, espn_s2=cookies['espn_s2'], swid=cookies['swid'])
        except:
            cookies = False

    if not cookies:
        league = ball.League(os.environ.get('BALL_ID'), 2020, username=os.environ.get('ESPN_USER'), password=os.environ.get('ESPN_PW'), save_cookies=True)
        

    keeps = {}
    for team in league.teams:
        team_keeps = []
        for player in team.roster:
            if is_eligible(player):
                team_keeps.append(player)

        keeps[team] = team_keeps

    print(pretty(keeps))
        
    
if __name__ == '__main__':
    keeper_eligible()
