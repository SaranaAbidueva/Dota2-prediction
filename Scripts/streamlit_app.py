import streamlit as st
import pandas as pd
# from make_prediction import pred
from API_handler import APIHandler
import json
import argparse
from config import config
import mlflow
from catboost import FeaturesData, Pool
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--root", default=config.default_root, type=str)
root = parser.parse_args().root

st.title('Predict Dota 2 Pro league game')

df = pd.read_csv('./deploy/Constants.Heroes.csv')
df['name_short'] = df['name'].apply(lambda x: x[14:])
df_teams = pd.read_csv('./deploy/collected_data.csv')[['radiant.name', 'dire.name']]
teams = pd.unique(pd.concat([df_teams['radiant.name'], df_teams['dire.name']]))

radiant_team_name = st.selectbox("Radiant team name", teams, key="radiant_name")
dire_team_name = st.selectbox("Dire team name", teams, key="dire_name")
def get_cat_features(X):
    hero_columns = []
    for side in ['radiant', 'dire']:
        hero_columns += [f'{side}.{i}_hero' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_account_id' for i in range(1, 6)]
    cat_features = ['patch', 'radiant.team_id', 'dire.team_id'] + hero_columns
    num_features = [x for x in X.columns.sort_values() if x not in cat_features]
    return cat_features, num_features

def get_features_for_predict(radiant_team_name, dire_team_name):
    api_handler = APIHandler()
    match_json = api_handler.get_live_match(radiant_team_name, dire_team_name)
    print(json.dumps(match_json, indent=4))

    # req = requests.get(f'https://api.opendota.com/api/live')
    # match_json = req.json()
    # match_json = match_json[0]
    # print(json.dumps(match_json, indent=4))

    match_id = match_json['match_id']
    team_id_radiant = match_json['team_id_radiant']
    team_id_dire = match_json['team_id_dire']
    players_df = pd.DataFrame(list(match_json['players']))
    players_df = players_df[['account_id', 'hero_id', 'team']]
    print(players_df)
    patch = api_handler.get_current_patch()

    pos_df = pd.read_csv(f'{root}/data/players_pos_data.csv')
    players_df = pd.merge(players_df, pos_df, on=['account_id'])
    players_df = players_df.drop(columns='match_datetime')

    players_df['cnt_games'], players_df['cnt_win'], players_df['cnt_games_patch'], players_df['cnt_win_patch'] = 0, 0, 0, 0

    for i, player in players_df.iterrows():
        players_df.loc[i, 'cnt_games'], players_df.loc[i, 'cnt_win'] = api_handler.get_current_winrate(
            player['account_id'],
            player['hero_id'],
            0)

        players_df.loc[i, 'cnt_games_patch'], players_df.loc[i, 'cnt_win_patch'] = api_handler.get_current_winrate(
            player['account_id'],
            player['hero_id'],
            patch_id=patch)
    players_df.to_csv(f'{root}/data/player_match.csv')
    features = {'radiant.team_id': team_id_radiant, 'dire.team_id': team_id_dire, 'patch': patch}
    for side in ['radiant', 'dire']:
        for pos in range(1, 6):
            features[f'{side}.{pos}_account_id'] = 0
            features[f'{side}.{pos}_hero'] = 0
            features[f'{side}.{pos}_cnt_games'] = 0
            features[f'{side}.{pos}_cnt_win'] = 0
            features[f'{side}.{pos}_wr'] = 0.0
            features[f'{side}.{pos}_cnt_games_patch'] = 0
            features[f'{side}.{pos}_cnt_win_patch'] = 0
            features[f'{side}.{pos}_wr_patch'] = 0.0

    for j, player in players_df.iterrows():
        if player.team == 0:
            side = 'radiant'
        elif player.team == 1:
            side = 'dire'
        pos = player['pos']
        features[f'{side}.{pos}_account_id'] = player['account_id']
        features[f'{side}.{pos}_hero'] = player['hero_id']
        features[f'{side}.{pos}_cnt_games'] = player['cnt_games']
        features[f'{side}.{pos}_cnt_win'] = player['cnt_win']
        features[f'{side}.{pos}_wr'] = player['cnt_win']/player['cnt_games'] if player['cnt_games'] > 0 else -1
        features[f'{side}.{pos}_cnt_games_patch'] = player['cnt_games_patch']
        features[f'{side}.{pos}_cnt_win_patch'] = player['cnt_win_patch']
        features[f'{side}.{pos}_wr_patch'] = player['cnt_win_patch'] / player['cnt_games_patch'] if player['cnt_games_patch'] > 0 else -1
    features = pd.DataFrame([features])
    pd.set_option('display.max_rows', 20)
    for i in range(83):
        print(features.dtypes.reset_index().iloc[i])
    features.to_csv(f'{root}/data/inference.csv', index=False)
    cat_features, num_features = get_cat_features(features)
    print(num_features)
    print(cat_features)
    features = Pool(data=features, cat_features=cat_features)
    # features = FeaturesData(
    #     num_feature_data=np.array(features[num_features], dtype=np.float32),
    #     cat_feature_data=np.array(np.array(np.array(features[cat_features], dtype=int), dtype=str), dtype=object))  # don't ask me wtf is this...
    return features


def inference(features):
    run_id = '6c9aad126fd24ce6b14dedb9c8ba39e8'
    model_uri = f"runs:/{run_id}/model"
    model = mlflow.catboost.load_model(model_uri)
    return model.predict_proba(features)



def make_predict():
    st.write(radiant_team_name)
    st.write(dire_team_name)
    features = get_features_for_predict(radiant_team_name, dire_team_name)
    if not features:
        pred = 'no game yet'
    else:
        pred = inference(features)
    st.write('Probability of Radiant win:')
    st.write(pred)
    col_rad, col_dire = st.columns(2)
    col_rad.write('Radiant')
    col_dire.write('Dire')




# st.write(pred)
st.button('Predict winner', on_click=make_predict)
