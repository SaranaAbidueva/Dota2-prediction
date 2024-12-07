import mlflow
import tempfile
import pandas as pd
import os
from catboost import CatBoostClassifier, Pool, FeaturesData, cv
import numpy as np


def get_cat_features(X):
    hero_columns = []
    for side in ['radiant', 'dire']:
        hero_columns += [f'{side}.{i}_hero' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_hero_variant' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_account_id' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_rank_tier' for i in range(1, 6)]
    cat_features = ['patch', 'radiant.team_id', 'dire.team_id'] + hero_columns
    num_features = [x for x in X.columns if x not in cat_features]
    return cat_features, num_features


client = mlflow.tracking.MlflowClient()
with mlflow.start_run() as run:
    # get best model
    experiment_id = run.info.experiment_id
    best_run = client.search_runs(
        experiment_id, order_by=["metrics.accuracy desc"], max_results=1
    )[0].data.to_dictionary()
    best_params = best_run['params']
    mlflow.log_params(best_params)

    # get last finished run for data preprocessing
    last_run_id = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"tags.mlflow.runName = 'data_preprocessing' and status = 'FINISHED'",
        order_by=["start_time DESC"]
    ).loc[0, 'run_id']
    # download train data from last run
    with tempfile.TemporaryDirectory() as tmpdir:
        mlflow.artifacts.download_artifacts(run_id=last_run_id, artifact_path='data/train.csv', dst_path=tmpdir)
        train = pd.read_csv(os.path.join(tmpdir, 'data/train.csv'))
        mlflow.artifacts.download_artifacts(run_id=last_run_id, artifact_path='data/test.csv', dst_path=tmpdir)
        test = pd.read_csv(os.path.join(tmpdir, 'data/test.csv'))

        # convert to Pool format
    features = [i for i in train.columns if i != 'target']
    cat_features, num_features = get_cat_features(train[features])
    cat_indexes = get_cat_features(train[features])
    train_features = FeaturesData(
        num_feature_data=np.array(train[num_features], dtype=np.float32),
        cat_feature_data=np.array(np.array(np.array(train[cat_features], dtype=int), dtype=str), dtype=object) # don't ask me wtf is this...
    )
    y_train = np.array(train['target'], dtype=bool)
    test_features = FeaturesData(
        num_feature_data=np.array(test[num_features], dtype=np.float32),
        cat_feature_data=np.array(np.array(np.array(test[cat_features], dtype=int), dtype=str), dtype=object)
    )
    y_test = np.array(test['target'], dtype=bool)

    train_dataset = Pool(data=train_features, label=y_train)
    test_dataset = Pool(data=test_features, label=y_test)
    print(best_params)

    model = CatBoostClassifier(iterations=int(best_params['iterations']),
                               learning_rate=float(best_params['learning_rate']),
                               loss_function=best_params['loss_function'],
                               depth=int(best_params['depth']),
                               verbose=False)
    model.fit(train_dataset)
    metrics = model.eval_metrics(data=test_dataset, metrics=['Accuracy', 'BalancedAccuracy', 'PRAUC', 'F1'])
    print(metrics)
    mlflow.log_metric("F1", metrics['F1'][-1])
    mlflow.log_metric("Accuracy", metrics['Accuracy'][-1])
    mlflow.log_metric("PRAUC", metrics['PRAUC'][-1])
    mlflow.log_metric("BalancedAccuracy", metrics['BalancedAccuracy'][-1])
    print(model.get_feature_importance(data=train_dataset, prettified=True))
    print([x for x in enumerate(num_features + cat_features)])
    mlflow.catboost.log_model(model, 'catboost')
