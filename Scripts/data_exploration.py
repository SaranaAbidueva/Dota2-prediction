import pandas as pd
from download_data import get_date
from tabulate import tabulate
from download_with_requests import get_match_players, get_person_winrate, get_match_patch
from tqdm import tqdm

dt = get_date()
df_picks = pd.read_csv(f'data/{dt}/draft_timings.csv')
df_teams = pd.read_csv(f'data/{dt}/teams.csv')
df_main = pd.read_csv(f'data/{dt}/main_metadata.csv')  # PK: match_id
df_players = pd.read_csv(f'data/{dt}/players.csv')


def head(df):
    print(tabulate(df.head(), headers='keys'))


df_all = pd.merge(df_main[['match_id', 'radiant_win', 'start_date_time', 'patch']], df_teams[['match_id', 'radiant.team_id', 'radiant.name', 'dire.team_id', 'dire.name']], on='match_id')
print(len(df_all))
head(df_all)

df_all = df_all.head()  #

player_info_list = []
for i, row in tqdm(df_all.iterrows()):
    match_id = row['match_id']
    match_players = df_players[df_players['match_id'] == match_id]
    patch = row['patch']
    match_players_dict = {'match_id': match_id}
    for j, player in match_players.iterrows():
        pos = player['player_slot']
        match_players_dict[f'pos_{pos}_account_id'] = player['account_id']
        match_players_dict[f'pos_{pos}_hero'] = player['hero_id']
        match_players_dict[f'pos_{pos}_hero_wr'], match_players_dict[f'pos_{pos}_hero_games'] = get_person_winrate(player['account_id'], player['hero_id'])
        match_players_dict[f'pos_{pos}_hero_wr_patch'], match_players_dict[f'pos_{pos}_hero_games_patch'] = get_person_winrate(player['account_id'], player['hero_id'], patch_id=patch)
    player_info_list.append(match_players_dict)

player_df = pd.DataFrame(player_info_list)

df_all = pd.merge(df_all, player_df, on='match_id')
df_all.to_csv('data/collected_data.csv')
head(df_all)
