import streamlit as st


st.title('Predict Dota 2 Pro league game')

st.text_input("Radiant team name", key="radiant_name")
st.text_input("Dire team name", key="dire_name")

st.text_input("Radiant pos1 hero", key="radiant.1_hero")
st.text_input("Dire pos1 hero", key="dire.1_hero")

st.text_input("Radiant pos1 hero variant", key="radiant.1_hero_variant")
st.text_input("Dire pos1 hero variant", key="dire.1_hero_variant")


st.text_input("Radiant team name", key="radiant_name")
