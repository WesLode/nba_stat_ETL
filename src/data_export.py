import json
import os
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguegamefinder, playergamelogs, \
    franchisehistory, commonplayerinfo,\
    boxscoreadvancedv2, boxscoredefensivev2,boxscorehustlev2,boxscorematchupsv3,\
    BoxScoreTraditionalV3, BoxScoreUsageV3,hustlestatsboxscore
from utils import export_to_file
from constant import JSON_OUTPUT_DIR

from api_call.data_per_game import get_box_score_per_game


import time
import pandas as pd
from api_call.static_data import get_all_team, get_all_player, \
    get_team_history, get_player_stat_per_game, get_game_summary

#################################################################################

def get_player_info(i):
    x = commonplayerinfo.CommonPlayerInfo(player_id=i).get_normalized_dict()
    export_to_file(str(i),x,output_dir=f'{JSON_OUTPUT_DIR}\\player_info')




def index_game(season):
    season_abbr = f"{str(season)}_{str(season +1)[-2:]}"
    print(season_abbr)
    game_pair = list()
    gmae_code = list()
    with open(f"{JSON_OUTPUT_DIR}\\gameSummary\\{season_abbr}.json",'r') as f1:
        game_data = json.load(f1)
        for game in game_data['LeagueGameFinderResults']:
            # print(game)
            # break
            if game['GAME_ID'] not in gmae_code:
                game_pair += [{
                    "season": game["SEASON_ID"],
                    "gameId" : game['GAME_ID'],
                    "matchUp": game['MATCHUP']
                }]
                gmae_code += [game['GAME_ID']]
            # game_pair[game['GAME_ID']]['Matchup'] += [game['MATCHUP']]
            # game_pair[game['GAME_ID']] = [game['MATCHUP']]
    
    export_to_file('game_code',game_pair,f"output\\{season_abbr}")


def dir_check(dir):
    return os.listdir(dir)

# boxscoreadvancedv2



if __name__ == "__main__":

    # Static
    # get_all_player()
    # get_all_team()

    # data per game
    get_box_score_per_game(season = 2021)
    # Continus
    # get_game_summary()
    # get_player_stat_per_game(from_season=2024)
    # get_team_history()
    # if True:

    # player_info_test()
    # x = box_score_advance()
    # print(x.get_available_data())

    # get_player_info(76003)   

    # Index
    # index_game(2023)