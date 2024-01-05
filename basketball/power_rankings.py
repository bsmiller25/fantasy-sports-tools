# powerrankings.py
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

def powerrankings(stats="last15"):

    # import league settings
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

    # get appropriate stats    
    if stats=='last30': stats='032024'
    if stats=='last15': stats='022024'
    if stats=='last7': stats='012024'
    if stats=='season': stats='002024'
    if stats=='proj': stats='102024'

    lstats = {}
    for team in league.teams:
        tstats = {'PTS': 0,
                   'REB': 0,
                   'AST': 0,
                   'STL': 0,
                   'BLK': 0,
                   '3PTM': 0,
                   'FGM': 0,
                   'FGA': 0,
                   'FTM': 0,
                   'FTA': 0,
                   'TO': 0,
                   }
        for player in team.roster:

            # skip injured players
            if player.injuryStatus == 'OUT':
                continue
            if player.lineupSlot == 'IR':
                continue
            
            # get the players average stats
            try:
                pstats = {'PTS': player.stats[stats]['avg']['PTS'],
                          'REB': player.stats[stats]['avg']['REB'],
                          'AST': player.stats[stats]['avg']['AST'],
                          'STL': player.stats[stats]['avg']['STL'],
                          'BLK': player.stats[stats]['avg']['BLK'],
                          '3PTM': player.stats[stats]['avg']['3PTM'],
                          'FGM': player.stats[stats]['avg']['FGM'],
                          'FGA': player.stats[stats]['avg']['FGA'],
                          'FTM': player.stats[stats]['avg']['FTM'],
                          'FTA': player.stats[stats]['avg']['FTA'],
                          'TO': player.stats[stats]['avg']['TO'],
                          }
                
                # add the player's stats to the team stats
                tstats = {k: tstats.get(k, 0) + pstats.get(k, 0) for k in set(tstats) & set(pstats)}

            except:
                continue

        lstats[team.team_abbrev] = tstats

    # make a dataframe
    ldf = pd.DataFrame(lstats).T
    ldf['FG%'] = ldf['FGM'] / ldf['FGA']
    ldf['FT%'] = ldf['FTM'] / ldf['FTA']

    # drop columns
    ldf.drop(['FTM', 'FTA', 'FGM', 'FGA'], axis=1, inplace=True)
        
    # convert to ranks
    ldfr = ldf.assign(**ldf.rank(axis = 0, ascending = True).astype(int))

    # flip TO
    ldfr['TO'] = ldfr['TO'].rank(ascending = False).astype(int)

    # sum cats
    ldfr['ROTO'] = ldfr.sum(axis=1)

    # order nicely
    ldfr = ldfr[['PTS', 'REB', 'AST', 'STL', 'BLK', '3PTM', 'FG%', 'FT%', 'TO', 'ROTO']].sort_values('ROTO', ascending=False)

    return(ldfr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stats', '-s', help='stats', type=str, default='proj')

    print(powerrankings())
    
