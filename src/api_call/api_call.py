import requests
import json 

import pandas as pd

api_link = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'

api_link = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news'

# api_link = 'https://stats.nba.com/stats/playbyplayv2?EndPeriod=0&GameID=0042300217&StartPeriod=0'
res = requests.get(api_link)

# Get Dict
response = json.loads(res.text)