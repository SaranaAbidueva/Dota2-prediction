import pandas as pd
from tabulate import tabulate
from tqdm import tqdm
from datetime import datetime
from loguru import logger
import sys
import warnings
import argparse
from config import config

# set up logging
# logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument("--year_month", default=config.default_year_month, type=str)
DT = parser.parse_args().year_month

parser.add_argument("--root", default=config.default_root, type=str)
root = parser.parse_args().root
logger.info(f'Data collecting from: {root}/data/{DT}')

df_teams = pd.read_csv(f'{root}/data/{DT}/teams.csv')
df_main = pd.read_csv(f'{root}/data/{DT}/main_metadata.csv')  # PK: match_id
df_players = pd.read_csv(f'{root}/data/{DT}/players.csv')
df_players_matches = pd.read_csv(f'{root}/data/{DT}/player_matches_history.csv')
df_players_matches['date'] = pd.to_datetime(df_players_matches['date'], format='%Y-%m-%d')


def head(df):
    print(tabulate(df.head(), headers='keys'))


df_all = pd.merge(df_main[['match_id', 'radiant_win', 'start_date_time', 'patch', 'leagueid']], df_teams[['match_id', 'radiant.team_id', 'radiant.name', 'dire.team_id', 'dire.name']], on='match_id')
head(df_all)
print('number of rows', len(df_all))


def get_person_winrate(account_id, hero_id, hero_variant, match_date_time, days=100, patch_id=None):
    match_date_time = datetime.strptime(match_date_time, '%Y-%m-%d %H:%M:%S')
    df_account_matches = df_players_matches[(df_players_matches['account_id'] == account_id) & (df_players_matches['hero_id'] == hero_id) & (df_players_matches['hero_variant'] == hero_variant) & (df_players_matches['date'] < match_date_time)]
    if patch_id:
        df_account_matches = df_account_matches[df_account_matches['patch'] == patch]
    if not df_account_matches.empty:
        cnt_win = df_account_matches[df_account_matches['win'] == 1]['win'].sum()
        cnt_lose = len(df_account_matches) - cnt_win
    else:
        cnt_win = 0
        cnt_lose = 0
    return cnt_win, cnt_lose


# get info about players.
player_info_list = []
for i, row in tqdm(df_all.iterrows()):
    match_id = row['match_id']
    match_players = df_players[df_players['match_id'] == match_id][['match_id', 'hero_id', 'hero_variant', 'account_id', 'player_slot', 'rank_tier']].drop_duplicates()
    patch = row['patch']
    match_players_dict = {'match_id': match_id}
    for j, player in match_players.iterrows():
        pos = int(player['player_slot'])
        side = 'radiant' if pos < 100 else 'dire'
        pos = pos + 1 if pos < 100 else pos - 128 + 1  # strange format of player_slot value
        account_id = int(player['account_id'])
        hero_id = player['hero_id']
        hero_variant = player['hero_variant']
        match_date_time = row['start_date_time']
        match_players_dict[f'{side}.{pos}_account_id'] = player['account_id']
        match_players_dict[f'{side}.{pos}_hero'] = player['hero_id']
        match_players_dict[f'{side}.{pos}_hero_variant'] = hero_variant
        match_players_dict[f'{side}.{pos}_hero_win'], match_players_dict[f'{side}.{pos}_hero_lose'] = get_person_winrate(account_id, hero_id, hero_variant, match_date_time)
        match_players_dict[f'{side}.{pos}_hero_win_patch'], match_players_dict[f'{side}.{pos}_hero_lose_patch'] = get_person_winrate(account_id, hero_id, hero_variant, match_date_time, patch_id=patch)
    player_info_list.append(match_players_dict)

player_df = pd.DataFrame(player_info_list)

df_all = pd.merge(df_all, player_df, on='match_id')
df_all.to_csv(f'{root}/data/collected_data.csv', index=False)
logger.info(f'Created {root}/data/collected_data.csv')
