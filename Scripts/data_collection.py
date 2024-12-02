import pandas as pd
from download_data import get_month
from tabulate import tabulate
# from download_with_requests import get_person_winrate_new
from tqdm import tqdm
import time
from datetime import datetime

# dt = get_month()
dt = '202411'
root = 'D:/projects/DOTA2 Prediction'
df_teams = pd.read_csv(f'{root}/data/{dt}/teams.csv')
df_main = pd.read_csv(f'{root}/data/{dt}/main_metadata.csv')  # PK: match_id
df_players = pd.read_csv(f'{root}/data/{dt}/players.csv')
df_players_matches = pd.read_csv(f'{root}/data/{dt}/player_matches_history.csv')
df_players_matches['date'] = pd.to_datetime(df_players_matches['date'], format='%Y-%m-%d')
df_ratings = pd.read_csv(f'{root}/data/players_leaderboard_ranks.csv')


def head(df):
    print(tabulate(df.head(), headers='keys'))


df_all = pd.merge(df_main[['match_id', 'radiant_win', 'start_date_time', 'patch', 'leagueid']], df_teams[['match_id', 'radiant.team_id', 'radiant.name', 'dire.team_id', 'dire.name']], on='match_id')
print(len(df_all))
head(df_all)

# df_all = df_all.head(7)


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


# problem: raiting is from one moment of time.
def get_person_raiting(account_id):
    df_account_raiting = df_ratings[df_ratings['account_id'] == account_id]
    if not df_account_raiting.empty:
        raiting = df_account_raiting.iloc[0]['leaderboard_rank']
    else:
        raiting = None
    return raiting

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
        match_players_dict[f'{side}.{pos}_rank_tier'] = player['rank_tier']
        match_players_dict[f'{side}.{pos}_leaderboard_rank'] = get_person_raiting(player['account_id'])
        match_players_dict[f'{side}.{pos}_hero_win'], match_players_dict[f'{side}.{pos}_hero_lose'] = get_person_winrate(account_id, hero_id, hero_variant, match_date_time)
        match_players_dict[f'{side}.{pos}_hero_win_patch'], match_players_dict[f'{side}.{pos}_hero_lose_patch'] = get_person_winrate(account_id, hero_id, hero_variant, match_date_time, patch_id=patch)
    player_info_list.append(match_players_dict)

player_df = pd.DataFrame(player_info_list)

df_all = pd.merge(df_all, player_df, on='match_id')
df_all.to_csv(f'{root}/data/collected_data.csv', index=False)
