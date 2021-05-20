# importar bibliotecas
import streamlit as st
from streamlit import caching
import matplotlib as plt
import pandas as pd
import numpy as np
import json

# Import firebase
from google.cloud import firestore
from google.oauth2 import service_account

#Configurando acesso ao firebase
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streamlit-cb45e")
doc_ref = db.collection(u'5porques')

# Link do arquivo com os dados
DATA_URL = "data.csv"

# Definição da sidebar
st.sidebar.title("Escolha a ação desejada")
inserir = st.sidebar.checkbox("Inserir ocorrência 5 Porquês")
analisar = st.sidebar.checkbox("Avaliar ocorrência 5 Porquês")
estatistica = st.sidebar.checkbox("Estatísticas de ocorrências")

#recarregar base de dados
rec = st.sidebar.button('Recarregar base de dados')
if rec:
	caching.clear_cache()

#Leitura dos dados, cache temporariamente desabilitado por conta da nserção de novos valores
@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	#colunas = data.columns
	posts_ref = db.collection("5porques_2")	
	# For a reference to a collection, we use .stream() instead of .get()
	for doc in posts_ref.stream():
		data = data.append(doc.to_dict(), ignore_index=True)
	#st.write(df.head())
	data['data'] = pd.to_datetime(data['data']).dt.date	
	return data

# Carrega dataframe e extrai suas colunas
dados = load_data()

# Lista vazia para input dos dados do formulário
lista = []
dic = {} #dicionario
submitted1=False

# Constantes
equipamentos = ['Uncoiler', 'Cupper']
gatilhos = [ 'Segurança', '10 minutos', '1 hora']
linhas = ['L571', 'L572', 'L581', 'Utilidades']
turnos = ['Turno A', 'Turno B', 'Turno C']
departamentos = ['Engenharia', 'Automação', 'Manutenção']
falhas = ['Máquina', 'Mão-de-obra', 'Método', 'Materiais', 'Meio ambiente', 'Medição', 'Outra']
deterioização = ['Forçada', 'Natural', 'Nenhuma']

# Imagem
st.image('Ambev.jpeg')
st.subheader('Aplicação 5 porques')
st.write('Selecione no menu lateral a opção desejada')

if inserir:
	st.subheader('Formulário para incluir ocorrência')

	with st.form('Form1'):
		dic['data'] = st.date_input('Data da ocorrência')
		dic['turno'] = st.selectbox('Selecione o turno', turnos )
		dic['departamento'] = st.selectbox('Selecione o departamento', departamentos)
		dic['linha'] = st.selectbox('Selecione a linha', linhas)
		dic['equipamento'] = st.selectbox('Selecione o equipamento', equipamentos)
		dic['gatilho'] = st.selectbox('Selecione o gatilho', gatilhos)
		dic['descrição anomalia'] = st.text_input('Descreva a anomalia', "")
		dic['ordem manutenção'] = st.text_input('Ordem de manutenção', "")
		dic['correção'] = st.text_input('Descreva a correção', "")
		dic['pq1'] = st.text_input('1) Por que?', "")
		dic['pq2'] = st.text_input('2) Por que?', "")
		dic['pq3'] = st.text_input('3) Por que?', "")
		dic['pq4'] = st.text_input('4) Por que?', "")
		dic['pq5'] = st.text_input('5) Por que?', "")
		dic['tipo de falha'] = st.multiselect('Selecione o tipo da falha', falhas)
		dic['falha deterioização'] = st.multiselect('Selecione o tipo da deterioização (falha)', deterioização)
		dic['tipo de correção'] = st.multiselect('Selecione o tipo da correção', falhas)
		dic['correção deterioização'] = st.multiselect('Selecione o tipo da deterioização (correção)', deterioização)
		dic['ações'] = st.text_input('Ações tomadas', "")
		dic['notas de manutenção'] = st.text_input('Notas de manutenção', "")
		dic['responsável identificação'] = st.text_input('Responsável pela identificação da anomalia', "")
		dic['responsável reparo'] = st.text_input('Responsável pela correção da anomalia', "")
		dic['verificado'] = 'não'
		submitted1 = st.form_submit_button('Enviar 5 Porquês')

	if submitted1:

		keys_values = dic.items()
		new_d = {str(key): str(value) for key, value in keys_values}
		doc_ref = db.collection("5porques_2").document(new_d['data'] + '_' + new_d['responsável identificação'])
		doc_ref.set(new_d)

if analisar:
	st.subheader('Selecione a data de início e fim para filtrar as cocorrências')

	col1, col2 = st.beta_columns(2)

	#col1.header("Início")
	inicio_filtro = col1.date_input("Início")

	#col2.header("Fim")
	fim_filtro = col2.date_input("Fim")
	st.write(dados[(dados['data'] >= inicio_filtro) & (dados['data'] <= fim_filtro)])

if estatistica:
	
	dados['turno'].plot.hist()
