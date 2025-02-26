# Dota 2 Pro games result prediction

Dota 2 is a highly competitive multiplayer online battle arena (MOBA) game that hosts numerous tournaments worldwide. 

**Objective** The goal is to predict the winner of a match based on various factors, including the draft, team composition, players' MMR ratings, and their win rates with the selected heroes. 

Such predictions could be valuable for better betting strategies.

**Data Sources** 
- Primary dataset: https://www.kaggle.com/datasets/bwandowando/dota-2-pro-league-matches-2023/data
- Additional information gathered using the OpenDota API: [OpenDota API Documentation](https://docs.opendota.com/#tag/matches) 

**Train Tutorial**

1. activate virtual env
```
venv\Scripts\activate
```
2. install requirements
```
pip install -r requirements.txt
```
3. change config.py:
- root - path to your project. 
- year_month - which data you want to download - for example, 202411 is November 2024.

4. Download data to local .csv files (takes few hours and around 700 Mb memory).
```
mlflow run . --entry-point data-downloading --env-manager local --experiment-name catboost2411 --run-name download_data
```

5. Transform data for training
```
mlflow run . --entry-point data-collecting --env-manager local --experiment-name catboost2411 --run-name transform_data
```

6. Find best hyperparameters with catboost
```
mlflow run . --entry-point hyperparameter-tuning --env-manager local --experiment-name catboost2411 --run-name hyperparameter_tuning
```

7. Check metrics (Accuracy, F1, ROC-AUC)
```
mlflow ui
```

8. Train best model
```
mlflow run . --entry-point train-best-model --env-manager local --experiment-name catboost2411 --run-name train_best_model
```
9. Run streamlit locally
```
streamlit run deploy/streamlit_app.py
```
10. Enter match ID (the same ID on bet sites)