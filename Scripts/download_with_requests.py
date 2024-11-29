import pandas as pd
import requests
from datetime import timedelta, datetime, date
from download_data import get_month
from tqdm import tqdm
import time


def get_match_players(match_id):
    req = requests.get(f'https://api.opendota.com/api/matches/{match_id}')
    match_json = req.json()
    match_players = [{'account_id': x['account_id'], 'nick': x['personaname'], 'hero_id': x['hero_id'],
                      'lane': x['lane']} for x in match_json['players']]
    return match_players


def get_person_winrate(account_id, hero_id, patch_id=None):
    params = {'date': 300, 'hero_id': hero_id}
    if patch_id:
        params['patch'] = patch_id
    req = requests.get(f'https://api.opendota.com/api/players/{account_id}/wl', params=params)
    if req.status_code == 200:
        cnt_win = req.json()['win']
        cnt_lose = req.json()['lose']
        return cnt_win, cnt_lose
    else:
        print(req.status_code)
        return None, None


def to_date(dt):
    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').date()


def unix_to_date(ts):
    dt = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').date()


# wins and loses before the match date
def get_person_winrate_new(account_id, hero_id, match_date_time, patch_id=None, days=100):
    today = date.today()
    match_date_time = to_date(match_date_time)
    date_param = (today - match_date_time).days + days
    params = {'date': date_param, 'hero_id': hero_id}
    if patch_id:
        params['patch'] = patch_id
    req = requests.get(f'https://api.opendota.com/api/players/{account_id}/matches', params=params)
    if req.status_code == 200:
        matches = req.json()
        cnt_win = sum([1 for match in matches if unix_to_date(match['start_time']) < match_date_time and
                       (match['player_slot'] < 100 and match['radiant_win']
                        or match['player_slot'] > 100 and not match['radiant_win'])])
        cnt_lose = len(matches) - cnt_win
        return cnt_win, cnt_lose
    else:
        print(req.status_code)
        return None, None


def download_player_data(account_id):
    """
    :param account_id:
    :return: list of dicts: {'account_id', 'start_time, 'win', 'patch'}
    """
    params = {'date': 100}
    req = requests.get(f'https://api.opendota.com/api/players/{account_id}/matches', params=params)
    if req.status_code == 200:
        matches = req.json()
        matches_list = []
        for match in matches:
            date = unix_to_date(match['start_time'])
            win = 1 if (match['player_slot'] < 100 and match['radiant_win']
                        or match['player_slot'] > 100 and not match['radiant_win']) else 0
            # TODO: NEED TO GET PATCH OTHERWISE, maybe function get_match_patch. but its one more call
            patch = 56
            hero_id = match['hero_id']
            match_dct = {'account_id': account_id, 'hero_id': hero_id, 'date': date, 'win': win, 'patch': patch}
            matches_list.append(match_dct)
        return matches_list
    else:
        print(req.status_code)
        return []


def download_all_players_data():
    """
    downloads matches of all players in 202411 folder for the past 100 days to csv
    """
    root = 'D:/projects/DOTA2 Prediction'
    dt = get_month()
    df_players = pd.read_csv(f'{root}/data/{dt}/players.csv')
    players_lst = df_players['account_id'].unique().astype(int)
    print('players count: ', len(players_lst))
    matches_list_all = []
    for i, account_id in enumerate(tqdm(players_lst)):
        matches_account = download_player_data(account_id)
        matches_list_all += matches_account
        if i % 10 == 0:
            df = pd.DataFrame(matches_list_all)
            df.to_csv(f'{root}/data/{dt}/my_player_matches.csv')
            time.sleep(10)


def get_match_patch(match_id):
    req = requests.get(f'https://api.opendota.com/api/matches/{match_id}')
    match_json = req.json()
    return match_json['patch']


match_id = 8013454282
account_id = 845344315
hero_id = 98

download_all_players_data()
# download_player_data(account_id)

# match_players = get_match_players(match_id)
# print(match_players)
# print([x['lane'] for x in match_players])

# for i, player in enumerate(match_players):
#     print(player, 'wr: ', get_person_winrate(player['account_id'], player['hero_id']))
#     patch = get_match_patch(match_id)
#     print(player, 'wr: ', get_person_winrate(player['account_id'], player['hero_id'], patch_id=patch))
