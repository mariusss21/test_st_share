# importar bibliotecas
import streamlit as st
import pandas as pd

DATA_URL = "https://drive.google.com/file/d/1pz0onHrxh5pJF9_coSCYcMGQE5Z6gVJR/view?usp=sharing"

@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	return data

df = load_data()

st.sidebar.title("Escolha a ação desejada")
if st.sidebar.checkbox("Inserir ocorrência 5 Porquês"):
	df = df.append(list(range(0,32)), ignore_index=True)
	st.write(df.head())
	df.to_csv(DATA_URL)


