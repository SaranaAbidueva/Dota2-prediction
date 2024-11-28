import kagglehub
from datetime import date


def get_date():
    today = date.today().strftime("%Y%m")
    return today

# Download the latest version
path = f"bwandowando/dota-2-pro-league-matches-{get_date()}"
dataset = kagglehub.dataset_download(path)