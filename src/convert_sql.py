from utilities.scan_df import create_postgres_sql_from_pandas
from utils import export_to_file

from data_export import get_all_player, get_game_summary,get_all_team

import pandas as pd
import json

with open('output\\data\\json_export\\player_stats\\player_stats_2024_25_playoffs.json'
          ,'r' , encoding='utf-8') as f1:
    output_text = json.load(f1)

team_df = pd.DataFrame(output_text['PlayerGameLogs'])
export_to_file(
    'team',
    create_postgres_sql_from_pandas(team_df, 'team'),
    output_dir='output\\sql',
    file_type='sql'
)