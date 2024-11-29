import pandas as pd
from download_data import get_date
from tabulate import tabulate
from download_with_requests import get_person_winrate
from tqdm import tqdm
import time

dt = get_date()
root = 'D:/projects/DOTA2 Prediction'
df_picks = pd.read_csv(f'{root}/data/{dt}/draft_timings.csv')
df_teams = pd.read_csv(f'{root}/data/{dt}/teams.csv')
df_main = pd.read_csv(f'{root}/data/{dt}/main_metadata.csv')  # PK: match_id
df_players = pd.read_csv(f'{root}/data/{dt}/players.csv')


def head(df):
    print(tabulate(df.head(), headers='keys'))


df_all = pd.merge(df_main[['match_id', 'radiant_win', 'start_date_time', 'patch']], df_teams[['match_id', 'radiant.team_id', 'radiant.name', 'dire.team_id', 'dire.name']], on='match_id')
print(len(df_all))
head(df_all)

df_all = df_all.head()  #

# get info about players.
# drawback: winrates are actual, i.e. from the future.
player_info_list = []
for i, row in tqdm(df_all.iterrows()):
    match_id = row['match_id']
    match_players = df_players[df_players['match_id'] == match_id]
    patch = row['patch']
    match_players_dict = {'match_id': match_id}
    for j, player in match_players.iterrows():
        pos = player['player_slot']
        side = 'radiant' if pos < 100 else 'dire'
        pos = pos + 1 if pos < 100 else pos - 128 + 1  # strange format of player_slot value
        account_id = int(player['account_id'])
        hero_id = player['hero_id']
        match_players_dict[f'{side}.{pos}_account_id'] = player['account_id']
        match_players_dict[f'{side}.{pos}_hero'] = player['hero_id']
        match_players_dict[f'{side}.{pos}_hero_win'], match_players_dict[f'{side}.{pos}_hero_lose'] = get_person_winrate(account_id, hero_id)
        match_players_dict[f'{side}.{pos}_hero_win_patch'], match_players_dict[f'{side}.{pos}_hero_lose_patch'] = get_person_winrate(account_id, hero_id, patch_id=patch)
    player_info_list.append(match_players_dict)
    time.sleep(10)

player_df = pd.DataFrame(player_info_list)

df_all = pd.merge(df_all, player_df, on='match_id')
df_all.to_csv(f'{root}/data/collected_data.csv')
head(df_all)
