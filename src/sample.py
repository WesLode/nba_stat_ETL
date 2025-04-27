import json
from utils import export_to_file

# with open('output/data/full_json/playerBoxscore.json','r',encoding='utf-8') as f1:
with open('output/data/full_json/full_player_stats.json','r',encoding='utf-8') as f1:
    data = json.load(f1)

col_table = []
cc =0
print(len(data))
# for i in data:
    # if '2023' in i['season']:
    # if True:
    # print(i)
    # for j in data['LeagueGameSummary']:
        # col_table += [j]
        # cc += 1
        # print(len(data['PlayerGameLogs']))
        # if cc >= 10:
            # break
# export_to_file('full_player_stats',col_table,output_dir='output/data/full_json')