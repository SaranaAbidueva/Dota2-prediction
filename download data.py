import kagglehub
from datetime import date
import shutil
import os

def get_date():
    today = date.today()
    return today.strftime("%Y%m")


def download_data():
    files_to_download = ['players', 'picks_bans', 'teams', 'main_metadata']
    dataset_url = f"bwandowando/dota-2-pro-league-matches-2023"
    for file in files_to_download:
        tgt_directory = f'data/{dt}'
        if not os.path.exists(tgt_directory):
            os.makedirs(tgt_directory)
        dataset_path = kagglehub.dataset_download(dataset_url, path=f'{dt}/{file}.csv')
        shutil.copy(dataset_path, tgt_directory)


dt = get_date()
download_data()
