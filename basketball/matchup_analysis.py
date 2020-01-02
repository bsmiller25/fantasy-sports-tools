# matchup_analysis.py
import os
import sys
import pandas as pd
import pdb
import espn_api.basketball as bball
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()


def matchup_projection(league, matchup, stats): 
    """Get projection for give matchup"""
    matchupPeriod = matchup.matchupPeriod

    if stats=='last30': stats='032020'
    if stats=='last15': stats='022020'
    if stats=='last7': stats='012020'
    if stats=='season': stats='002020'
    if stats=='proj': stats='102020'

    # find the start scoring period
    match_start = (1 - league.start_date.weekday() + 7 * (matchupPeriod - 1),
                   league.start_date - timedelta(league.start_date.weekday()) + timedelta(weeks=matchupPeriod - 1))
    match_dates = [(match_start[0] + i, match_start[1] + timedelta(i)) for i in list(range(7))]
    
    
    remaining_dates = [md for md in match_dates if md[1] >= datetime.today().date()]

    proj_stats = {}
    if matchup.home_team_cats:
        proj_stats[matchup.home_team] = matchup.home_team_cats
        proj_stats[matchup.away_team] = matchup.away_team_cats
    else:
        proj_stats[matchup.home_team] = {'PTS': {'score': 0},
                                         'REB': {'score': 0},
                                         'AST': {'score': 0},
                                         'STL': {'score': 0},
                                         'BLK': {'score': 0},
                                         '3PTM': {'score': 0},
                                         'TO': {'score': 0},
                                         'FTM': {'score': 0},
                                         'FTA': {'score': 0},
                                         'FGM': {'score': 0},
                                         'FGA': {'score': 0},
                                         'FT%': {'score': 0},
                                         'FG%': {'score': 0},
                                         }
        proj_stats[matchup.away_team] = {'PTS': {'score': 0},
                                         'REB': {'score': 0},
                                         'AST': {'score': 0},
                                         'STL': {'score': 0},
                                         'BLK': {'score': 0},
                                         '3PTM': {'score': 0},
                                         'TO': {'score': 0},
                                         'FTM': {'score': 0},
                                         'FTA': {'score': 0},
                                         'FGM': {'score': 0},
                                         'FGA': {'score': 0},
                                         'FT%': {'score': 0},
                                         'FG%': {'score': 0},
                                         }

    for day in remaining_dates:
        sched = league._get_nba_schedule(day[0])

        for team in [matchup.home_team, matchup.away_team]:
            for player in team.roster:
                if player.injuryStatus == 'OUT':
                    continue
                if player.proTeam in sched.keys():
                    if stats in player.stats.keys():
                        proj_stats[team]['PTS']['score'] += player.stats[stats]['avg']['PTS']
                        proj_stats[team]['REB']['score'] += player.stats[stats]['avg']['REB']
                        proj_stats[team]['AST']['score'] += player.stats[stats]['avg']['AST']
                        proj_stats[team]['STL']['score'] += player.stats[stats]['avg']['STL']
                        proj_stats[team]['BLK']['score'] += player.stats[stats]['avg']['BLK']
                        proj_stats[team]['3PTM']['score'] += player.stats[stats]['avg']['3PTM']
                        proj_stats[team]['TO']['score'] += player.stats[stats]['avg']['TO']
                        proj_stats[team]['FTM']['score'] += player.stats[stats]['avg']['FTM']
                        proj_stats[team]['FTA']['score'] += player.stats[stats]['avg']['FTA']
                        proj_stats[team]['FGM']['score'] += player.stats[stats]['avg']['FGM']
                        proj_stats[team]['FGA']['score'] += player.stats[stats]['avg']['FGA']
                        try:
                            proj_stats[team]['FT%']['score'] = (proj_stats[team]['FTM']['score'] /
                                                                         proj_stats[team]['FTA']['score'])
                        except ZeroDivisionError:
                            proj_stats[team]['FT%']['score'] = 0
                        try:
                            proj_stats[team]['FG%']['score'] = (proj_stats[team]['FGM']['score'] /
                                                                         proj_stats[team]['FGA']['score'])
                        except ZeroDivisionError:
                            proj_stats[team]['FG%']['score'] = 0
                            
    # display
    home = pd.DataFrame(proj_stats[matchup.home_team]).T
    away =  pd.DataFrame(proj_stats[matchup.away_team]).T
    final = pd.DataFrame({matchup.home_team.team_abbrev: home['score'],
                          matchup.away_team.team_abbrev: away['score']})
    score_stats = ['PTS', 'REB', 'AST', 'STL', 'BLK', '3PTM', 'FG%', 'FT%', '-TO']
    home_score = 0
    for stat in score_stats:
        # for stats you want a lot of
        if stat[0] != '-':
            comp = final.loc[stat, :]
            if comp[0] > comp[1]:
                home_score += 1
            elif comp[0] == comp[1]:
                home_score += 0.5
        # for stats you want less of
        else:
            comp = final.loc[stat[1:], :]
            if comp[0] < comp[1]:
                home_score += 1
            elif comp[0] == comp[1]:
                home_score += 0.5
    final = final.append(pd.DataFrame({comp.index[0]: home_score, comp.index[1]: 9 - home_score}, index=['Score']))    

    return(final)

def week_analysis(team_id=None, matchupPeriod=None, stats='season', verbose=False):
    """Get a matchup report or matchup reports"""
    league = bball.League(os.environ.get('BBALL_ID'), 2020, username=os.environ.get('ESPN_USER'), password=os.environ.get('ESPN_PW'))

    if not matchupPeriod:
        matchupPeriod = league.currentMatchupPeriod

    if team_id:
        matchup = [i for i in league.scoreboard(matchupPeriod) if (i.home_team.team_id == team_id or
                                                                   i.away_team.team_id == team_id)][0]
        matchup.matchupPeriod = matchupPeriod
        report = matchup_projection(league, matchup, stats)
        if verbose: print(report)
        reports = [report]
    else:
        reports = []
        for matchup in league.scoreboard(matchupPeriod):
            matchup.matchupPeriod = matchupPeriod
            report = matchup_projection(league, matchup, stats)
            if verbose: print(report)
            reports.append(report)

    return(reports)
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--period', '-p', help='matchup period', type=int, default=None)
    parser.add_argument('--team', '-t', help='team id', type=int, default=None)
    parser.add_argument('--stats', '-s', help='stats', type=str, default='season')

    args = parser.parse_args()
    
    week_analysis(matchupPeriod=args.period,
                  team_id=args.team,
                  stats=args.stats,
                  verbose=True)    

