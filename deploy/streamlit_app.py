import streamlit as st
import pandas as pd

st.title('Predict Dota 2 Pro league game')

st.text_input("Radiant team name", key="radiant_name")
st.text_input("Dire team name", key="dire_name")

df = pd.DataFrame('Constants.Heroes.csv')
df['name_short'] = df['name'].apply(lambda x: x[14:])

# Select box for heroes
for side in ['Radiant', 'Dire']:
    for i in range(1, 6):
        option = st.selectbox(f'{side} pos{i} hero', df['name_short'], key=f"{side}.{i}_hero")

for side in ['Radiant', 'Dire']:
    for i in range(1, 6):
        option = st.selectbox(f'{side} pos{i} hero', list(range(1, 6)), key=f"{side}.{i}_hero_variant")
# st.text_input("Radiant pos1 hero", key="radiant.1_hero")
st.text_input("Dire pos1 hero", key="dire.1_hero")

st.text_input("Radiant pos1 hero variant", key="radiant.1_hero_variant")
st.text_input("Dire pos1 hero variant", key="dire.1_hero_variant")

