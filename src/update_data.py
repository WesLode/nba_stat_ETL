import json
import os
from utils import export_to_file, get_data_sample

read_dir = 'output\\data\\json_export\\player_stats'

append_dic = 'output\\data\\json_export\\player_stats.json'

file_index = False
if file_index == False:
    with open('player_stat_index.json','r', encoding='utf-8') as f2:
        file_index = set(json.load(f2))
else:
    with open(append_dic,'r', encoding='utf-8') as f2:
        temp_json = json.load(f2)
    file_index = set()
    for table in temp_json:
        for r in temp_json[table]:
            file_index.add(r['GAME_ID'])

print(len(file_index))
with open(append_dic,'r', encoding='utf-8') as f2:
    gameSumm = json.load(f2)


for i in os.listdir(read_dir):
    with open(f'{read_dir}\\{i}','r',encoding='utf-8') as f1:
        temp_data = json.load(f1)
    for lt in temp_data['PlayerGameLogs']:
        if lt['GAME_ID'] not in file_index:
            gameSumm['PlayerGameLogs'] += [lt]

export_to_file('player_stats',gameSumm,'output\\data\\json_export')

print(len(gameSumm['PlayerGameLogs']))