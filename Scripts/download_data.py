import kagglehub
from datetime import date
import shutil
import os


def get_month():
    today = date.today()
    return today.strftime("%Y%m")


def download_data():
    files_to_download = ['draft_timings', 'teams', 'main_metadata', 'players']
    dataset_url = f"bwandowando/dota-2-pro-league-matches-2023"
    tgt_directory = f'D:/projects/DOTA2 Prediction/data/{dt}'
    if not os.path.exists(tgt_directory):
        os.makedirs(tgt_directory)
    for file in files_to_download:
        dataset_path = kagglehub.dataset_download(dataset_url, path=f'{dt}/{file}.csv')
        shutil.copy(dataset_path, tgt_directory)


dt = get_month()
download_data()
