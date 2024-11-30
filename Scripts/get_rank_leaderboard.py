import requests
import pandas as pd

account_id = 1178619702
root = 'D:\projects\DOTA2 Prediction'
df_players = pd.read_csv(f'{root}/data/{dt}/players.csv')
players_lst = df_players['account_id'].unique().astype(int)
lst = []
for i, account_id in enumerate(players_lst):
    req = requests.get(f'https://api.opendota.com/api/players/{account_id}')
    ans = req.json()
    if 'leaderboard_rank' in ans:
        leaderboard_rank = ans['leaderboard_rank']
    else:
        leaderboard_rank = None
    rank_tier = ans['rank_tier']
    lst.append({'account_id': account_id, 'leaderboard_rank': leaderboard_rank, 'rank_tier': rank_tier})
    if i % 20 == 0:
        df = pd.DataFrame(lst)
        df.to_csv(f'{root}/data/players_leaderboard_ranks.csv', index=False)


# req = requests.get(f'https://api.opendota.com/api/players/{account_id}')
# print(req.json())
# ans = req.json()
# if 'leaderboard_rank' in ans:
#     leaderboard_rank = ans['leaderboard_rank']
# else:
#     leaderboard_rank = None
# print(leaderboard_rank)
