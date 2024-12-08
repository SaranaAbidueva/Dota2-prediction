import kagglehub
import shutil
import os
from loguru import logger
import sys
import warnings
import argparse
from config import config
from API_handler import APIHandler


def download_from_kaggle():
    files_to_download = ['teams', 'main_metadata', 'players']
    dataset_url = f"bwandowando/dota-2-pro-league-matches-2023"
    tgt_directory = f'{root}/data/{DT}'
    if not os.path.exists(tgt_directory):
        os.makedirs(tgt_directory)
    try:
        for file in files_to_download:
            dataset_path = kagglehub.dataset_download(dataset_url, path=f'{DT}/{file}.csv')
            shutil.copy(dataset_path, tgt_directory)
    except kagglehub.exceptions.KaggleApiHTTPError:
        raise kagglehub.exceptions.KaggleApiHTTPError('no data for this month yet')


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

api_handler = APIHandler(yearmonth=DT)
api_handler.download_all_players_data()
logger.info(f'Finish downloading API data')
