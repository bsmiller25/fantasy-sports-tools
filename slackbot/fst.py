import os
import sys
import slack

sys.path.append('.')

from basketball import matchup_analysis

client = slack.WebClient(token=os.environ.get('SLACK_TOKEN'))

# also requires 'BBALL_ID', 'ESPN_USER', and 'ESPN_PW' env vars
proj = matchup_analysis.week_analysis(stats='last30', verbose=False)

for output in proj:
    response = client.chat_postMessage(
        channel='#fantasy_basketball',
        text=str(output))

