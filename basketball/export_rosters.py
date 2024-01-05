# Matchup_analysis.py
import os
import sys
import pandas as pd
import pdb
import espn_api.basketball as bball
import argparse
import pickle
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

def export_rosters(team_id=None, verbose=False):
    """Get rosters"""

    # check for existing pickled cookies
    try:
        fileObj = open('../cookies.pkl', 'rb')
        cookies = pickle.load(fileObj)
    except:
        cookies = False

    if cookies:
        league = bball.League(os.environ.get('BBALL_ID'), 2024, espn_s2=cookies['espn_s2'], swid=cookies['swid'])

    if not cookies:
        league = bball.League(os.environ.get('BBALL_ID'), 2024, username=os.environ.get('ESPN_USER'), password=os.environ.get('ESPN_PW'), save_cookies=True)


    # get rosters
    teams = []
    players = []
    for team in league.teams:
        for player in team.roster:
            teams.append(team.team_abbrev)
            players.append(player.name)
    rosters = pd.DataFrame(data={'team': teams, 'player': players})
    rosters.to_csv('rosters.csv', index=False)
    

if __name__ == '__main__':
    export_rosters()
    
