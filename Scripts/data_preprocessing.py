import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool, FeaturesData
from sklearn.model_selection import train_test_split
from loguru import logger
import argparse
from config import config
import mlflow
import optuna
from mlflow.data.sources import LocalArtifactDatasetSource

parser = argparse.ArgumentParser()

parser.add_argument("--root", default=config.default_root, type=str)
root = parser.parse_args().root
df = pd.read_csv(f'{root}/data/collected_data.csv')
df = df.sort_values(by='start_date_time')
df['start_date_time'] = df['start_date_time'].str.split(' ').str.get(0)
df['day'] = df['start_date_time'].str.split('-').str.get(2)
df['month'] = df['start_date_time'].str.split('-').str.get(1)

print(df.describe())
print(df.isna().sum())
print('all data size before dropna', len(df))
df = df.dropna()
print('all data size after dropna', len(df))
y = df['radiant_win']
X = df.drop(['match_id', 'radiant_win', 'radiant.name', 'dire.name', 'start_date_time'], axis=1)

mlflow.log_metric('full_data_size', len(X))
mlflow.log_metric('features_count', len(X.columns))


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


cat_features, num_features = get_cat_features(X)
print(cat_features[:10])
print(num_features[:10] + num_features[-2:])


X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False)

mlflow.log_metric('train_size', X_train.shape[0])
mlflow.log_metric('test_size', X_test.shape[0])
mlflow.log_metric('number of categorical features', len(cat_features))
mlflow.log_metric('number of numerical features', len(num_features))
print('number of categorical features', len(cat_features))
print('number of numerical features', len(num_features))

cat_dct = {}
for f in cat_features:
    cat_dct[f] = int
X_train = X_train.astype(cat_dct)
X_test = X_test.astype(cat_dct)
cat_dct = {}
for f in cat_features:
    cat_dct[f] = str
X_train = X_train.astype(cat_dct)
X_test = X_test.astype(cat_dct)

train = X_train.assign(target=y_train)
mlflow.log_text(train.to_csv(index=False), 'data/train.csv')
dataset_source_link = mlflow.get_artifact_uri('data/train.csv')
dataset = mlflow.data.from_pandas(train, name='train', targets="target", source=LocalArtifactDatasetSource(dataset_source_link))
mlflow.log_input(dataset)

test = X_test.assign(target=y_test)
mlflow.log_text(test.to_csv(index=False), 'data/test.csv')
dataset_source_link = mlflow.get_artifact_uri('data/test.csv')
dataset = mlflow.data.from_pandas(train, name='test', targets="target", source=LocalArtifactDatasetSource(dataset_source_link))
mlflow.log_input(dataset)

logger.info('Data preprocessing finished')

train_features = FeaturesData(
        num_feature_data=np.array(X_train[num_features], dtype=np.float32),
        cat_feature_data=np.array(np.array(np.array(X_train[cat_features], dtype=int), dtype=str), dtype=object)  # don't ask me wtf is this...
    )
test_features = FeaturesData(
        num_feature_data=np.array(X_test[num_features], dtype=np.float32),
        cat_feature_data=np.array(np.array(np.array(X_test[cat_features], dtype=int), dtype=str), dtype=object)
    )

y_train = np.array(y_train, dtype=bool)
y_test = np.array(y_test, dtype=bool)

train_pool = Pool(data=train_features, label=y_train)
test_pool = Pool(data=test_features, label=y_test)

catboost = CatBoostClassifier(
    iterations=10,
    learning_rate=0.5,
    depth=5,
    loss_function='Logloss')

catboost.fit(train_pool)

metrics = catboost.eval_metrics(test_pool, metrics=['Accuracy', 'Logloss', 'PRAUC', 'F1'], plot=True)
print(metrics)
print('percent of 1 in y_test: ', round(100.*sum(y_test)/len(y_test), 2))
print(catboost.get_feature_importance(data=train_pool, prettified=True))
print([x for x in enumerate(num_features + cat_features)])
