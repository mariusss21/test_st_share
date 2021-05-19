# importar bibliotecas
import streamlit as st
import pandas as pd

# Link do arquivo com os dados
DATA_URL = "data.csv"

#Leitura dos dados, cache temporariamente desabilitado por conta da nserção de novos valores
#@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	return data

# Carrega dataframe e extrai suas colunas
df = load_data()
colunas = df.columns

#st.write(df.head())

# Definição da sidebar
st.sidebar.title("Escolha a ação desejada")
st.sidebar.checkbox("Inserir ocorrência 5 Porquês")
st.sidebar.checkbox("Avaliar ocorrência 5 Porquês")

# Lista vazia para input dos dados do formulário
lista = []
submitted1=False

# Constantes
equipamentos = ['Uncoiler', 'Cupper']
gatilhos = ['10 minutos', 'Segurança', '1 hora']
linhas = ['L571', 'L572', 'L581', 'Utilidades']
turnos = ['Turno A', 'Turno B', 'Turno C']
departamentos = ['Engenharia', 'Automação', 'Manutenção']


with st.form('Form1'):
	lista.append(st.date_input('Data da ocorrência'))
	lista.append(st.selectbox('Selecione o turno', turnos ))
	lista.append(st.selectbox('Selecione o departamento', departamentos))
	lista.append(st.selectbox('Selecione a linha', linhas))
	lista.append(st.selectbox('Selecione o equipamento', equipamentos))]
	lista.append(st.selectbox('Selecione o gatilho', gatilhos))


	lista.append(st.slider(label='Select intensity', min_value=0, max_value=100))
	submitted1 = st.form_submit_button('Enviar 5 Porquês')

if submitted1:
	df2 = pd.DataFrame(lista).T
	df2.columns = colunas
	df = pd.concat([df, df2], join='inner', ignore_index=True)
	df.to_csv(DATA_URL, index=False)

#st.write(df.head())

