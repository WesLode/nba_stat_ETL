import json
import os
from api_call.static_data import get_game_summary, get_player_log_per_game
from utils import export_to_file, get_data_sample
from nba_api.stats.endpoints import boxscoreadvancedv2

def update_file():
    read_dir = 'output\\data\\full_json'

    current_season = 2024
    current_season_id = []
    for i in range(1,7):
        current_season_id.extend([f'{i}{str(current_season)}'])

    update_gameId_List, current_season_game = get_game_summary(from_season=current_season)
    update_list = []

    with open(f'{read_dir}//gameSummary.json','r',encoding='utf-8') as f1:
        data = json.load(f1)
        for i in data:
            if i['SEASON_ID'] in current_season_id:

                if i['GAME_ID'] in update_gameId_List:
                    update_gameId_List.remove(i['GAME_ID'])

        for j in current_season_game:
            for i in current_season_game[j]:
                if i['GAME_ID'] in update_gameId_List:
                    update_list.extend([i])

        print(f'Update Game: {len(update_list)}')
        data.extend(update_list)
    print(update_gameId_List)

    # export_to_file('gameSummary',data, output_dir=read_dir)

    if True:
        result = get_player_log_per_game(from_season=current_season, to_season=current_season)


        update_list = []
        with open(f'output/data/json_export/player_stats/player_stats_2024_25_playoffs.json','r',encoding='utf-8') as f1:
            data = json.load(f1)
            for j in data:
                for i in data[j]:
                    if i['GAME_ID'] in update_gameId_List:
                        update_list.extend([i])
            print(len(update_list))

        if len(update_list) >0:
            with open(f'{read_dir}//full_player_stats.json','r',encoding='utf-8') as f1:
                data_og = json.load(f1)
                print(f'Original count: {len(data_og)}')
                index_id = set()
                for i in data_og:
                    index_id.add(i['GAME_ID'])

                player_stats_update = 0 
                print(f'update_list :{len(update_list)}')
                for j in update_list:
                    if j['GAME_ID'] not in index_id:
                        data_og += [j]
                        player_stats_update += 1
                # data_og.extend(update_list)
                
            print(player_stats_update)
            print(f'Updated count: {len(data_og)}')
        
        export_to_file('full_player_stats',data_og, output_dir=read_dir)

    if True:
        update_list = []
        with open(f'{read_dir}//playerBoxscore.json','r',encoding='utf-8') as f1:
            data = json.load(f1)
            print(f'Original count: {len(data)}')
            index_id = set()
            for i in data:
                index_id.add(i['id'])
            
            for j in update_gameId_List:
                if j not in index_id:
                    api_result = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=j).get_normalized_dict()
                    print(j)
                    update_list.extend([{
                        "id":j,
                        "PlayerStats":api_result['PlayerStats'],
                        "TeamStats":api_result['TeamStats']
                    }])
                
        
        if len(update_list) >0:
            data.extend(update_list)
            print(f'Update count: {len(data)}')
            # export_to_file('playerBoxscore',data,output_dir=read_dir)

if __name__ == "main":
    update_file()