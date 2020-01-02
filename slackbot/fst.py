import os
import sys
import datetime
import slack
import pandas as pd
from tabulate import tabulate

sys.path.append('.')

from basketball import matchup_analysis

client = slack.WebClient(token=os.environ.get('SLACK_TOKEN'))

# also requires 'BBALL_ID', 'ESPN_USER', and 'ESPN_PW' env vars
proj = matchup_analysis.week_analysis(stats='last30', verbose=False)

if datetime.datetime.now().time() < datetime.time(11): 
    parent = client.chat_postMessage(
        channel='#fantasy_basketball',
        text='Pre-waiver projections for {}'.format(datetime.date.today())
    )
else:
    parent = client.chat_postMessage(
        channel='#fantasy_basketball',
        text='Post-waiver projections for {}'.format(datetime.date.today())
    )

for output in proj:
    response = client.chat_postMessage(
        channel='#fantasy_basketball',
        thread_ts=parent['ts'],
        text=str(tabulate(output, headers='keys', tablefmt='orgtbl', floatfmt='.2f')))

    
