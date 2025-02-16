import pandas as pd
from sklearn.model_selection import train_test_split
from loguru import logger
import argparse
from config import config
import mlflow
from tqdm import tqdm
import sys
import warnings
from datetime import datetime
from tabulate import tabulate
from mlflow.data.sources import LocalArtifactDatasetSource

parser = argparse.ArgumentParser()

parser.add_argument("--root", default=config.default_root, type=str)
root = parser.parse_args().root
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


df = pd.read_csv(f'{root}/data/collected_data.csv')
df = df.sort_values(by='start_date_time')
df['start_date_time'] = df['start_date_time'].str.split(' ').str.get(0)
df['day'] = df['start_date_time'].str.split('-').str.get(2)
df['month'] = df['start_date_time'].str.split('-').str.get(1)

print(df.describe())
print(df.isna().sum())
print('all data size before dropna', len(df))
df = df.dropna()
print('all data size after dropna', len(df))
y = df['radiant_win']
X = df.drop(['match_id', 'radiant_win', 'radiant.name', 'dire.name', 'start_date_time'], axis=1)

mlflow.log_metric('full_data_size', len(X))
mlflow.log_metric('features_count', len(X.columns))


def get_cat_features(X):
    hero_columns = []
    for side in ['radiant', 'dire']:
        hero_columns += [f'{side}.{i}_hero' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_hero_variant' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_account_id' for i in range(1, 6)]
        # hero_columns += [f'{side}.{i}_rank_tier' for i in range(1, 6)]
    cat_features = ['patch', 'radiant.team_id', 'dire.team_id'] + hero_columns
    num_features = [x for x in X.columns if x not in cat_features]
    return cat_features, num_features


cat_features, num_features = get_cat_features(X)
print(cat_features[:10])
print(num_features[:10] + num_features[-2:])


X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False)

mlflow.log_metric('train_size', X_train.shape[0])
mlflow.log_metric('test_size', X_test.shape[0])
mlflow.log_metric('number of categorical features', len(cat_features))
mlflow.log_metric('number of numerical features', len(num_features))
print('number of categorical features', len(cat_features))
print('number of numerical features', len(num_features))

cat_dct = {}
for f in cat_features:
    cat_dct[f] = int
X_train = X_train.astype(cat_dct)
X_test = X_test.astype(cat_dct)
cat_dct = {}
for f in cat_features:
    cat_dct[f] = str
X_train = X_train.astype(cat_dct)
X_test = X_test.astype(cat_dct)

logger.info('Data loading to mlflow server')

train = X_train.assign(target=y_train)
mlflow.log_text(train.to_csv(index=False), 'data/train.csv')
dataset_source_link = mlflow.get_artifact_uri('data/train.csv')
dataset = mlflow.data.from_pandas(train, name='train', targets="target", source=LocalArtifactDatasetSource(dataset_source_link))
mlflow.log_input(dataset)

test = X_test.assign(target=y_test)
mlflow.log_text(test.to_csv(index=False), 'data/test.csv')
dataset_source_link = mlflow.get_artifact_uri('data/test.csv')
dataset = mlflow.data.from_pandas(train, name='test', targets="target", source=LocalArtifactDatasetSource(dataset_source_link))
mlflow.log_input(dataset)

logger.info('Data preprocessing finished')
