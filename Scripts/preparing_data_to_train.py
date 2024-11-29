import pandas as pd

df = pd.read_csv('data/prepared_data.csv')
y = df['radiant_win']
X = df.drop(['match_id', 'radiant_win', 'radiant.name', 'dire.name'])
