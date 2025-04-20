import json
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguegamefinder, playergamelogs
from utils import export_to_file
from constant import JSON_OUTPUT_DIR

import time
import pandas as pd

def get_all_team():
    nba_teams = teams.get_teams()
    # x = pd.DataFrame(nba_teams)
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
    return True

def get_game_season(season):
    h= str(season +1)[-2:]
    print(f"{str(season)}-{str(h)}")
    gamefinder = leaguegamefinder.LeagueGameFinder(
        league_id_nullable= "00",
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

def index_game(season):
    season_abbr = f"{str(season)}_{str(season +1)[-2:]}"
    print(season_abbr)
    game_pair = list()
    gmae_code = list()
    with open(f"output\\{season_abbr}\\game.json",'r') as f1:
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


def get_player_stat_per_game(from_season = 1983, to_season = 2024, season_Type = 'All'):
    if season_Type == 'All':
        season_Type = ['Regular Season', 'Playoffs', 'PlayIn']


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

if __name__ == "__main__":
    # get_all_player()
    # get_all_team()
    # get_game_summary()
    get_player_stat_per_game()

