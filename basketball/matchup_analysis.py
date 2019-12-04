# matchup_analysis.py
import os
import sys
import pandas as pd
import pdb
import espn_api.basketball as bball
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()


def matchup_projection(league, matchup): 
    """Get projection for give matchup"""
    matchupPeriod = matchup.matchupPeriod
    
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

        # update home team projected stats
        for player in matchup.home_team.roster:
            if player.injuryStatus == 'OUT':
                continue
            if player.proTeam in sched.keys():
                if '022020' in player.stats.keys():
                    proj_stats[matchup.home_team]['PTS']['score'] += player.stats['022020']['avg']['PTS']
                    proj_stats[matchup.home_team]['REB']['score'] += player.stats['022020']['avg']['REB']
                    proj_stats[matchup.home_team]['AST']['score'] += player.stats['022020']['avg']['AST']
                    proj_stats[matchup.home_team]['STL']['score'] += player.stats['022020']['avg']['STL']
                    proj_stats[matchup.home_team]['BLK']['score'] += player.stats['022020']['avg']['BLK']
                    proj_stats[matchup.home_team]['3PTM']['score'] += player.stats['022020']['avg']['3PTM']
                    proj_stats[matchup.home_team]['TO']['score'] += player.stats['022020']['avg']['TO']
                    proj_stats[matchup.home_team]['FTM']['score'] += player.stats['022020']['avg']['FTM']
                    proj_stats[matchup.home_team]['FTA']['score'] += player.stats['022020']['avg']['FTA']
                    proj_stats[matchup.home_team]['FGM']['score'] += player.stats['022020']['avg']['FGM']
                    proj_stats[matchup.home_team]['FGA']['score'] += player.stats['022020']['avg']['FGA']
                    proj_stats[matchup.home_team]['FT%']['score'] = (proj_stats[matchup.home_team]['FTM']['score'] /
                                                                     proj_stats[matchup.home_team]['FTA']['score'])
                    proj_stats[matchup.home_team]['FG%']['score'] = (proj_stats[matchup.home_team]['FGM']['score'] /
                                                                     proj_stats[matchup.home_team]['FGA']['score'])
        # update away team projected stats
        for player in matchup.away_team.roster:
            if player.injuryStatus == 'OUT':
                continue
            if player.proTeam in sched.keys():
                if '022020' in player.stats.keys():
                    proj_stats[matchup.away_team]['PTS']['score'] += player.stats['022020']['avg']['PTS']
                    proj_stats[matchup.away_team]['REB']['score'] += player.stats['022020']['avg']['REB']
                    proj_stats[matchup.away_team]['AST']['score'] += player.stats['022020']['avg']['AST']
                    proj_stats[matchup.away_team]['STL']['score'] += player.stats['022020']['avg']['STL']
                    proj_stats[matchup.away_team]['BLK']['score'] += player.stats['022020']['avg']['BLK']
                    proj_stats[matchup.away_team]['3PTM']['score'] += player.stats['022020']['avg']['3PTM']
                    proj_stats[matchup.away_team]['TO']['score'] += player.stats['022020']['avg']['TO']
                    proj_stats[matchup.away_team]['FTM']['score'] += player.stats['022020']['avg']['FTM']
                    proj_stats[matchup.away_team]['FTA']['score'] += player.stats['022020']['avg']['FTA']
                    proj_stats[matchup.away_team]['FGM']['score'] += player.stats['022020']['avg']['FGM']
                    proj_stats[matchup.away_team]['FGA']['score'] += player.stats['022020']['avg']['FGA']
                    proj_stats[matchup.away_team]['FT%']['score'] = (proj_stats[matchup.away_team]['FTM']['score'] /
                                                                     proj_stats[matchup.away_team]['FTA']['score'])
                    proj_stats[matchup.away_team]['FG%']['score'] = (proj_stats[matchup.away_team]['FGM']['score'] /
                                                                     proj_stats[matchup.away_team]['FGA']['score'])
                    
    # display
    home = pd.DataFrame(proj_stats[matchup.home_team]).T
    away =  pd.DataFrame(proj_stats[matchup.away_team]).T
    final = pd.DataFrame({matchup.home_team: home['score'],
                          matchup.away_team: away['score']})
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

def week_analysis(team_id=None, matchupPeriod=None, verbose=False):
    """Get a matchup report or matchup reports"""
    league = bball.League(os.environ.get('BBALL_ID'), 2020, username=os.environ.get('ESPN_USER'), password=os.environ.get('ESPN_PW'))

    if not matchupPeriod:
        matchupPeriod = league.currentMatchupPeriod

    if team_id:
        matchup = [i for i in league.scoreboard(matchupPeriod) if (i.home_team.team_id == team_id or
                                                                   i.away_team.team_id == team_id)][0]
        matchup.matchupPeriod = matchupPeriod
        report = matchup_projection(league, matchup)
        if verbose: print(report)
        reports = [report]
    else:
        reports = []
        for matchup in league.scoreboard(matchupPeriod):
            matchup.matchupPeriod = matchupPeriod
            report = matchup_projection(league, matchup)
            if verbose: print(report)
            reports.append(report)

    return(reports)
        

if __name__ == '__main__':

    matchupPeriod = None
    team_id = None
    
    if len(sys.argv) >= 2:
        matchupPeriod = int(sys.argv[1])

    if len(sys.argv) >= 3:
        team_id = int(sys.argv[2])
        
    week_analysis(matchupPeriod=matchupPeriod,
                  team_id=team_id,
                  verbose=True)    

