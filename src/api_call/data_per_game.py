import os
from nba_api.stats.static import teams, players
# from nba_api.stats import 
from nba_api.stats.endpoints import playbyplayv3, \
    playergamelogs,playergamelog, franchiseplayers, franchisehistory,\
    playbyplayv2, leaguegamelog, leaguegamefinder, boxscoreadvancedv2,\
    boxscoreadvancedv3
import pandas as pd
import json
import time
import requests

from utils import export_to_file, retry, get_data_sample, make_dir
from constant import  JSON_OUTPUT_DIR

# @retry(max_retries=4, delay=0.5, exceptions=(ConnectionError, TimeoutError))
def get_box_score_per_game(season=2024, dirr = JSON_OUTPUT_DIR, table = 'gameSummary'):
    json_data = f"{str(season)}_{str(season +1)[-2:]}"
    dirr= f'{dirr}\\{table}'
    make_dir(f'{dirr.replace('gameSummary','boxScoreAdvance')}\\{json_data}')
    with open(f'{dirr}\\{json_data}.json','r',encoding='utf-8') as f1:
        temp_data = json.load(f1)

    filter_seasonId = '22024'
    collect_result = set()
    for i in os.listdir(f'{JSON_OUTPUT_DIR}\\boxScoreAdvance\\{json_data}'):
        collect_result.add(i.replace('.json',''))
    print(len(collect_result))
    for i in temp_data['LeagueGameFinderResults']:
        if i['GAME_ID'] not in collect_result:
            print(i['MATCHUP'])
            time.sleep(1)
            api_result = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=i['GAME_ID'])

            # season 1998 is a locked out season with missing game
            if api_result.get_normalized_dict()['PlayerStats'] == [] and i['SEASON_ID'] not in ["21998","11998","31998","41998"]:
                print('Result not availabel..')
                break
            export_to_file(i['GAME_ID'],api_result.get_normalized_dict(),output_dir=f'{JSON_OUTPUT_DIR}\\boxScoreAdvance\\{json_data}')
            collect_result.add(i['GAME_ID'])