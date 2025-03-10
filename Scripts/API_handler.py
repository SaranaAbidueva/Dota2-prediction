import pandas as pd
import requests
from datetime import datetime
from tqdm import tqdm
import time


def unix_to_date(ts):
    dt = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').date()


def to_date(dt):
    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').date()


class APIHandler:
    def __init__(self, yearmonth='202501', primary_url='https://api.opendota.com/api', root='D:\projects\DOTA2 Prediction'):
        self.primary_url = primary_url
        self.yearmonth = yearmonth
        self.root = root

    def get_match_players(self, match_id):
        req = requests.get(f'{self.primary_url}/matches/{match_id}')
        match_json = req.json()
        match_players = [{'account_id': x['account_id'], 'nick': x['personaname'], 'hero_id': x['hero_id'],
                          'lane': x['lane']} for x in match_json['players']]
        return match_players

    def download_player_data(self, account_id):
        """
        :param account_id:
        :return: list of dicts: {'account_id', 'hero_id', 'start_time, 'win', 'patch', 'hero_variant'}
        """
        params = {'date': 100}
        req = requests.get(f'{self.primary_url}/players/{account_id}/matches', params=params)
        if req.status_code == 200:
            matches = req.json()
            matches_list = []
            for match in matches:
                date = unix_to_date(match['start_time'])
                win = 1 if (match['player_slot'] < 100 and match['radiant_win']
                            or match['player_slot'] > 100 and not match['radiant_win']) else 0
                # TODO: NEED TO GET PATCH OTHERWISE, maybe function get_match_patch. but its one more API call
                patch = 56
                hero_id = match['hero_id']
                hero_variant = match['hero_variant']
                match_dct = {'account_id': account_id, 'hero_id': hero_id, 'date': date, 'win': win, 'patch': patch,
                             'hero_variant': hero_variant}
                matches_list.append(match_dct)
            return matches_list
        else:
            print(req.status_code)
            return []

    def download_all_players_data(self):
        """
        downloads matches of all players in 202411 folder for the past 100 days to csv
        """
        dt = self.yearmonth
        df_players = pd.read_csv(f'{self.root}/data/{dt}/players.csv')
        players_lst = df_players['account_id'].unique().astype(int)
        print('players count: ', len(players_lst))
        matches_list_all = []
        for i, account_id in enumerate(tqdm(players_lst)):
            if i < 1449:
                continue
            matches_account = self.download_player_data(account_id)
            matches_list_all += matches_account
            if i % 10 == 0:
                df = pd.DataFrame(matches_list_all)
                df.to_csv(f'{self.root}/data/{dt}/player_matches_history2.csv')
                time.sleep(10)

    def get_live_match(self, radiant_team_name, dire_team_name):
        req = requests.get(f'{self.primary_url}/live')
        match_json = req.json()
        for game in match_json:
            if game['team_name_radiant'] == radiant_team_name and game['team_name_dire'] == dire_team_name:
                return game

    def get_current_patch(self):
        req = requests.get(f'{self.primary_url}/constants/patch')
        patch_json = req.json()
        patch_df = pd.DataFrame(patch_json)
        return max(patch_df['id'])

    def get_current_winrate(self, account_id, hero_id, patch_id):
        params = {'limit': 1000, 'hero_id': hero_id, 'patch': patch_id} if patch_id \
            else {'limit': 1000, 'hero_id': hero_id}
        req = requests.get(f'{self.primary_url}/players/{account_id}/heroes', params=params)
        wr_json = req.json()[0]
        return wr_json['games'], wr_json['win']


