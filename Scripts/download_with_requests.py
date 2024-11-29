import requests


def get_match_players(match_id):
    req = requests.get(f'https://api.opendota.com/api/matches/{match_id}')
    match_json = req.json()
    match_players = [{'account_id': x['account_id'], 'nick': x['personaname'], 'hero_id': x['hero_id'],
                      'lane': x['lane']} for x in match_json['players']]
    print(match_json['radiant_team'])
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

# def get_person_winrate_new(account_id, hero_id, patch_id=None, match_date_time):
#     params = {'date': 300, 'hero_id': hero_id}
#     if patch_id:
#         params['patch'] = patch_id
#     req = requests.get(f'https://api.opendota.com/api/players/{account_id}/wl', params=params)
#     if req.status_code == 200:
#         cnt_win = req.json()['win']
#         cnt_lose = req.json()['lose']
#         return cnt_win, cnt_lose
#     else:
#         print(req.status_code)
#         return None, None


def get_match_patch(match_id):
    req = requests.get(f'https://api.opendota.com/api/matches/{match_id}')
    match_json = req.json()
    return match_json['patch']


match_id = 8013454282
account_id = 845344315
hero_id = 98
print(get_person_winrate(account_id, hero_id))


# match_players = get_match_players(match_id)
# print(match_players)
# print([x['lane'] for x in match_players])

# for i, player in enumerate(match_players):
#     print(player, 'wr: ', get_person_winrate(player['account_id'], player['hero_id']))
#     patch = get_match_patch(match_id)
#     print(player, 'wr: ', get_person_winrate(player['account_id'], player['hero_id'], patch_id=patch))
