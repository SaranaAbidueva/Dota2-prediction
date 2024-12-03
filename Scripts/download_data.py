import kagglehub
from datetime import date
import shutil
import os
from API_handler import api_handler


def download_from_kaggle():
    files_to_download = ['teams', 'main_metadata', 'players']
    dataset_url = f"bwandowando/dota-2-pro-league-matches-2023"
    tgt_directory = f'{root}/data/{dt}'
    if not os.path.exists(tgt_directory):
        os.makedirs(tgt_directory)
    for file in files_to_download:
        dataset_path = kagglehub.dataset_download(dataset_url, path=f'{dt}/{file}.csv')
        shutil.copy(dataset_path, tgt_directory)


root = 'D:/projects/DOTA2 Prediction'
dt = date.today().strftime("%Y%m")
download_from_kaggle()
api_handler.download_all_players_data()
api_handler.get_rank_leaderboard()
