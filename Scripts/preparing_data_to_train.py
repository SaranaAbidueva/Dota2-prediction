import pandas as pd
from catboost import CatBoostClassifier
# from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import train_test_split

df = pd.read_csv('data/prepared_data.csv')
df = df.sort_values(by='start_date_time')
y = df['radiant_win']
X = df.drop(['match_id', 'radiant_win', 'radiant.name', 'dire.name'])
print(X.columns)

hero_columns = [f'radiant.{i}_hero' for i in range(1, 6)]
hero_columns += [f'radiant.{i}_account_id' for i in range(1, 6)]
hero_columns += [f'dire.{i}_hero' for i in range(1, 6)]
hero_columns += [f'dire.{i}_account_id' for i in range(1, 6)]
cat_features = ['patch', 'radiant.team_id', 'dire.team_id'] + hero_columns

X_train, y_train, X_test, y_test = train_test_split(X, y)
catboost = CatBoostClassifier()
catboost.fit(X_train, y_train, cat_features=cat_features)

y_test = catboost.predict(X_test)
