import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool, FeaturesData
# from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import train_test_split
from tabulate import tabulate

root = 'D:/projects/DOTA2 Prediction'
df = pd.read_csv(f'{root}/data/collected_data.csv')
df = df.sort_values(by='start_date_time')
df['start_date_time'] = df['start_date_time'].str.split(' ').str.get(0)
df['day'] = df['start_date_time'].str.split('-').str.get(2)
df['month'] = df['start_date_time'].str.split('-').str.get(1)

print(df.describe())
print(df.isna())
print(len(df))
df = df.dropna()
print(len(df))
y = df['radiant_win']
X = df.drop(['match_id', 'radiant_win', 'radiant.name', 'dire.name', 'start_date_time'], axis=1)

hero_columns = []
for side in ['radiant', 'dire']:
    hero_columns += [f'{side}.{i}_hero' for i in range(1, 6)]
    hero_columns += [f'{side}.{i}_hero_variant' for i in range(1, 6)]
    hero_columns += [f'{side}.{i}_account_id' for i in range(1, 6)]
    hero_columns += [f'{side}.{i}_rank_tier' for i in range(1, 6)]
cat_features = ['patch', 'radiant.team_id', 'dire.team_id'] + hero_columns
num_features = [x for x in X.columns if x not in cat_features]

print(cat_features)
print(num_features)

X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False)
train_features = FeaturesData(
        num_feature_data=np.array(X_train[num_features], dtype=np.float32),
        cat_feature_data=np.array(np.array(np.array(X_train[cat_features], dtype=int), dtype=str), dtype=object)
    )
test_features = FeaturesData(
        num_feature_data=np.array(X_test[num_features], dtype=np.float32),
        cat_feature_data=np.array(np.array(np.array(X_test[cat_features], dtype=int), dtype=str), dtype=object)
    )
catboost = CatBoostClassifier(
    iterations=2,
    learning_rate=1,
    depth=2,
    loss_function='Logloss')
y_train = np.array(y_train, dtype=bool)
y_test = np.array(y_test, dtype=bool)

# catboost.fit(train_features, y_train)
# train_pool = Pool(X_train, y_train, cat_features=cat_features)
# test_pool = Pool(X_test, y_test, cat_features=cat_features)

train_pool = Pool(data=train_features, label=y_train)
test_pool = Pool(data=test_features, label=y_test)


catboost.fit(train_pool)

metrics = catboost.eval_metrics(test_pool, metrics=['Accuracy', 'Logloss', 'PRAUC', 'F1'], plot=True)
print(metrics)
