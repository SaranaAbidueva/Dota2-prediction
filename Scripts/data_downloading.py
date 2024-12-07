import kagglehub
from datetime import date
import shutil
import os
from API_handler import api_handler
from loguru import logger
import sys
import warnings
import argparse
from config import config

def download_from_kaggle():
    files_to_download = ['teams', 'main_metadata', 'players']
    dataset_url = f"bwandowando/dota-2-pro-league-matches-2023"
    tgt_directory = f'{root}/data/{DT}'
    if not os.path.exists(tgt_directory):
        os.makedirs(tgt_directory)
    for file in files_to_download:
        dataset_path = kagglehub.dataset_download(dataset_url, path=f'{DT}/{file}.csv')
        shutil.copy(dataset_path, tgt_directory)


logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument("--year_month", default=config.default_year_month, type=str)
DT = parser.parse_args().year_month

parser.add_argument("--root", default=config.default_root, type=str)
root = parser.parse_args().root
logger.info(f'Start downloading data to: {root}/data/{DT}')

download_from_kaggle()
logger.info(f'Finish downloading Kaggle data. Start downloading API data')
api_handler.download_all_players_data()
api_handler.get_rank_leaderboard()
logger.info(f'Finish downloading API data')
