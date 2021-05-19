# importar bibliotecas
import streamlit as st
import pandas as pd

DATA_URL = "data.csv"

#@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	return data

df = load_data()
colunas = df.columns

#st.write(df.head())

st.sidebar.title("Escolha a ação desejada")
st.sidebar.checkbox("Inserir ocorrência 5 Porquês")
st.sidebar.checkbox("Avaliar ocorrência 5 Porquês")

lista = []
submitted1=False

with st.form('Form1'):
	lista.append(st.date_input('Data da ocorrência'))
	lista.append(st.selectbox('Selecione o turno', ['Turno A', 'Turno B', 'Turno C']))
	lista.append(st.selectbox('Selecione o departamento', ['Engenharia', 'Automação']))
	lista.append(st.selectbox('Selecione a linha', ['L571', 'L572', 'L581', 'Utilidades']))
	if lista[3] == 'L571':
    		lista.append(st.selectbox('Selecione o equipamento', ['1', '2', '3', '4']))
	elif lista[3] == 'L572':
    		lista.append(st.selectbox('Selecione o equipamento', ['5', '6', '7', '8']))
	else:
    		lista.append(st.selectbox('Selecione o equipamento', ['5', '6']))

	lista.append(st.slider(label='Select intensity', min_value=0, max_value=100))
	submitted1 = st.form_submit_button('Enviar 5 Porquês')

if submitted1:
	df2 = pd.DataFrame(lista).T
	df2.columns = colunas
	df = pd.concat([df, df2], join='inner', ignore_index=True)
	df.to_csv(DATA_URL, index=False)

#st.write(df.head())

