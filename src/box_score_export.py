from nba_api.stats.endpoints import playbyplayv2
import json
from utils import export_to_file
from constant import JSON_OUTPUT_DIR
import time
import os


# with open('output\\2023_24\\game_code.json','r') as f1:
#     game_code_map = json.load(f1)
# countter =0
# record=0
# for i in game_code_map:
        
#     x = playbyplayv2.PlayByPlayV2(game_id=i['gameId'],get_request=True, timeout=30).get_normalized_dict()
#     export_to_file(i['gameId'], x['PlayByPlay'],output_dir=  f'{JSON_OUTPUT_DIR}\\playbyplay')
#     countter +=1
#     record +=1
#     if record%3 == 0:
#         time.sleep(10)
#     if countter >=100:
#         break

x = os.listdir('output\\data\\json_export\\player_info')

print(len(x))