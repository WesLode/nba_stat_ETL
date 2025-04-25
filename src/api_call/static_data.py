import json
import os
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguegamefinder, playergamelogs, \
    franchisehistory, commonplayerinfo,\
    boxscoreadvancedv2, boxscoredefensivev2,boxscorehustlev2,boxscorematchupsv3,\
    BoxScoreTraditionalV3, BoxScoreUsageV3,hustlestatsboxscore
from utils import export_to_file
from constant import JSON_OUTPUT_DIR

import time
import pandas as pd




# Get All Current Team 
def get_all_team():
    nba_teams = teams.get_teams()
    export_to_file('nba_team',nba_teams, output_dir=JSON_OUTPUT_DIR)

    return nba_teams


# Return listed []
def get_all_player(status=None):
    if status is None:
        result = players.get_players()
    if status == 'active':
        result = players.get_active_players()
    export_to_file("All_players",result,output_dir = JSON_OUTPUT_DIR)
    return result

# Get All team History
def get_team_history():
    x = franchisehistory.FranchiseHistory()
    table_name = x.get_available_data()

    for i in table_name:
        export_to_file(i,x.get_normalized_dict()[str(i)], output_dir=JSON_OUTPUT_DIR)

# Get player stats per game
def get_player_stat_per_game(from_season = 1983, to_season = 2024, season_Type = 'All'):
    if season_Type == 'All':
        season_Type = ['Regular Season', 'Playoffs', 'PlayIn', 'IST']
    elif season_Type not in ['Regular Season', 'Playoffs', 'PlayIn', 'IST']:
        print('Incorrent Season Type')
        return False
    else:
        season_Type = [season_Type]

    for season in range(from_season,to_season+1):

        for st in season_Type:
            result = playergamelogs.PlayerGameLogs(
                    season_nullable=f'{str(season)}-{str(str(season +1)[-2:])}',
                    # season_type_nullable= "Regular Season"
                    # season_type_nullable= "Playoffs"
                    season_type_nullable= [st]
                    ).get_normalized_dict()
            export_to_file(
                f'player_stats_{str(season)}_{str(str(season +1)[-2:])}_{st.replace(' ','').lower()}',
                result,
                output_dir=f"{JSON_OUTPUT_DIR}\\player_stats"
            )

    return True        

def get_game_summary(from_season = 1983, to_season = 2024):
    if from_season <1983 or to_season >2024:
        print('data not available for the input year')
        return False
    batch_size = 0
    for season in range(from_season,to_season+1):
        get_game_season(season)
        batch_size += 1
        if batch_size>=3:
            print('loading...')
            time.sleep(1)
            batch_size = 0
    print('Game Summary export at outpou/data/json_export/gameSummary.')
    return True

def get_game_season(season=2024, league_id = "00"):
    h= str(season +1)[-2:]
    print(f"{str(season)}-{str(h)}")
    gamefinder = leaguegamefinder.LeagueGameFinder(
        league_id_nullable= league_id,
            # nba = "00"
            # aba = "01"
            # wnba = "10"
            # summer_league = "15"
            # g_league = "20"
        # team_id_nullable='1610612744',
        season_nullable = f"{str(season)}-{str(h)}",
    )

    export_to_file(
        f'{str(season)}_{str(h)}',
        gamefinder.get_normalized_dict(),
        output_dir=f"{JSON_OUTPUT_DIR}\\gameSummary"
    )

    # return gamefinder.get_normalized_dict()
    return gamefinder.get_data_frames()

