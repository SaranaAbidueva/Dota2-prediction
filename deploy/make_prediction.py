import mlflow
import tempfile
import pandas as pd
import os
from catboost import CatBoostClassifier, Pool, FeaturesData
import numpy as np


def get_cat_features(X):
    hero_columns = []
    for side in ['radiant', 'dire']:
        hero_columns += [f'{side}.{i}_hero' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_hero_variant' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_account_id' for i in range(1, 6)]
        # hero_columns += [f'{side}.{i}_rank_tier' for i in range(1, 6)]
    cat_features = ['patch', 'radiant.team_id', 'dire.team_id'] + hero_columns
    num_features = [x for x in X.columns if x not in cat_features]
    return cat_features, num_features


def get_data_from_team(radiant_team_name, dire_team_name,):
    data_dict = {'radiant.team_id': radiant_team_name, 'dire.team_id': dire_team_name}
    data_dict['patch'] = 56
    data_dict['']


with mlflow.start_run() as run:
    # get best model
    experiment_id = run.info.experiment_id
    version = mlflow.MlflowClient().get_registered_model('catboost').latest_versions[0].version
    model = mlflow.catboost.load_model(model_uri=f"models:/catboost/{version}")

    last_run_id = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"tags.mlflow.runName = 'data_preprocessing' and status = 'FINISHED'",
        order_by=["start_time DESC"]
    ).loc[0, 'run_id']



    # convert to Pool format
    features = [i for i in test.columns if i != 'target']
    cat_features, num_features = get_cat_features(test[features])

    test_features = FeaturesData(
        num_feature_data=np.array(test[num_features], dtype=np.float32),
        cat_feature_data=np.array(np.array(np.array(test[cat_features], dtype=int), dtype=str), dtype=object)
    )
    y_test = np.array(test['target'], dtype=bool)

    test_dataset = Pool(data=test_features, label=y_test)
    print(cat_features)
    print(num_features)
    pred = model.predict_proba(test_dataset.slice([0]))
    print(pred)
    print(model.predict(test_dataset.slice([0])))

