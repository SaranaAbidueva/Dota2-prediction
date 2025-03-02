import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool, FeaturesData, cv
from loguru import logger
import mlflow
import optuna
import tempfile
import os


def get_cat_features(X):
    hero_columns = []
    for side in ['radiant', 'dire']:
        hero_columns += [f'{side}.{i}_hero' for i in range(1, 6)]
        hero_columns += [f'{side}.{i}_account_id' for i in range(1, 6)]
    cat_features = ['radiant.team_id', 'dire.team_id', 'patch'] + hero_columns
    num_features = [x for x in X.columns.sort_values() if x not in cat_features]
    return cat_features, num_features


def objective(trial):
    # hyperparameters
    params = {
        "loss_function": trial.suggest_categorical('loss_function', ["Logloss"]),
        "custom_metric": ["F1", "AUC", "Accuracy", "BalancedAccuracy"],
        "depth": trial.suggest_int("depth", 2, 6),
        "learning_rate": trial.suggest_float("learning_rate", 0.12, 0.3),
        "verbose": False,
        "iterations": trial.suggest_int("iterations", 100, 200)
    }
    with mlflow.start_run(nested=True):
        mlflow.log_params(params)
        # params.update(eval_metric=['auc', 'error'])
        print(params)
        cv_results = cv(pool=cv_dataset,
                        params=params,
                        fold_count=5,
                        plot=True)
        accuracy = cv_results['test-Accuracy-mean'].iloc[-1]

        mlflow.log_metric("F1", cv_results['test-F1-mean'].iloc[-1])
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("AUC", cv_results['test-AUC-mean'].iloc[-1])
        mlflow.log_metric("AUC", cv_results['test-BalancedAccuracy-mean'].iloc[-1])
        logger.info(f"Attempt: {trial.number}, Accuracy: {accuracy}")
        error = cv_results['test-Logloss-mean'].iloc[-1]
        return error


mlflow.end_run()
with mlflow.start_run() as run:
    # get experiment id
    experiment_id = run.info.experiment_id

    # get last finished run for data preprocessing
    last_run_id = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"tags.mlflow.runName = 'transform_data' and status = 'FINISHED'",
        order_by=["start_time DESC"]
    ).loc[0, 'run_id']

    # download train data from last run
    with tempfile.TemporaryDirectory() as tmpdir:
        mlflow.artifacts.download_artifacts(run_id=last_run_id, artifact_path='data/train.csv', dst_path=tmpdir)
        train = pd.read_csv(os.path.join(tmpdir, 'data/train.csv'))
    # convert to Pool format
    features = [i for i in train.columns if i != 'target']
    cat_features, num_features = get_cat_features(train[features])
    print(num_features)
    print(cat_features)
    cat_indexes = get_cat_features(train[features])
    train_features = FeaturesData(
            num_feature_data=np.array(train[num_features], dtype=np.float32),
            cat_feature_data=np.array(np.array(np.array(train[cat_features], dtype=int), dtype=str), dtype=object),  # don't ask me wtf is this...
            num_feature_names=num_features,
            cat_feature_names=cat_features
        )
    y_train = np.array(train['target'], dtype=bool)
    cv_dataset = Pool(data=train_features, label=y_train)
    logger.info('Starting optuna study')

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=4)
    best_trial = study.best_trial

    logger.info(f'Optimization finished, best params: {best_trial.params}')
    mlflow.log_params(best_trial.params)

    logger.info(f'Best trial Accuracy: {1 - best_trial.value}')
    mlflow.log_metric('accuracy', 1 - study.best_value)
