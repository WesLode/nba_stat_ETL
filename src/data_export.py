import json
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import leaguegamefinder
from utils import export_to_file

import time
import pandas as pd

def get_all_team():
    nba_teams = teams.get_teams()
    # x = pd.DataFrame(nba_teams)
    export_to_file('nba_team',nba_teams,'output')


    return nba_teams

# Return listed []
def get_all_player(status=None):
    if status is None:
        return players.get_players()
    if status == 'active':
        return players.get_active_players()

def get_game(season):
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
        # timeout=400
        
    )

    # return gamefinder.get_normalized_dict()
    export_to_file('game',gamefinder.get_normalized_dict(),f"output\\{str(season)}_{str(h)}")

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



if __name__ == "__main__":
    # y = find_one_game()
    y= get_all_team()
    # result = y[y.GAME_ID == '0052400121']
    # y=range(2023,2025)
    y=range(1983,2025)
    for i in y:
        # index_game(i)
        # break
        get_game(i)
        print('pause')
        time.sleep(1)

    print(y)
