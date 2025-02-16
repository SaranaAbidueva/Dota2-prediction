import streamlit as st
import pandas as pd
# from make_prediction import pred


st.title('Predict Dota 2 Pro league game')

df = pd.read_csv('./deploy/Constants.Heroes.csv')
df['name_short'] = df['name'].apply(lambda x: x[14:])
df_teams = pd.read_csv('./data/collected_data.csv')[['radiant.name', 'dire.name']]
teams = pd.unique(df_teams['radiant.name'] + df_teams['dire.name'])

st.selectbox("Radiant team name", teams, key="radiant_name")
st.selectbox("Dire team name", teams, key="dire_name")

# Select box for heroes
for side in ['Radiant', 'Dire']:
    for i in range(1, 6):
        option = st.selectbox(f'{side} pos{i} hero', df['name_short'], key=f"{side}.{i}_hero")
        option = st.selectbox(f'{side} pos{i} hero variant', list(range(1, 6)), key=f"{side}.{i}_hero_variant")

st.write('The winner probabilities:')
# st.write(pred)
st.write(st.session_state['radiant.1_hero'])
