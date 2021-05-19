# importar bibliotecas
import streamlit as st
import pandas as pd
import numpy as np
import json
import time

# Import firebase
from google.cloud import firestore
from google.oauth2 import service_account

#Configurando acesso ao firebase
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streamlit-cb45e")
doc_ref = db.collection(u'5porques')

#timestamp
ts = time.time()

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

# Titulo da aplicação
st.title('Formulário 5 porques')

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
	submitted1 = st.form_submit_button('Enviar 5 Porquês')

if submitted1:
	#df2 = pd.DataFrame(lista).T
	#df2.columns = colunas
	#st.write(df2.head())
	#df2.astype('category')
	#dados = df2.to_dict()
	keys_values = dic.items()
	new_d = {str(key): str(value) for key, value in keys_values}
	doc_ref.add(new_d)
	#st.write(df2.pivot(columns=colunas))
	
	#df = pd.concat([df, df2], join='inner', ignore_index=True)
	#df.to_csv(DATA_URL, index=False)
	# This time, we're creating a NEW post reference for Apple
	#doc_ref = db.collection("5porques").document("teste")

	# And then uploading some data to that reference
	#doc_ref.set({
	#"title": "Apple",
	#"url": "www.apple.com"
	#})

st.write(df.head())


# referencias 
# https://blog.streamlit.io/secrets-in-sharing-apps/
# https://blog.streamlit.io/streamlit-firestore/
# https://blog.streamlit.io/streamlit-firestore-continued/

'''
	lista.append(st.date_input('Data da ocorrência'))
	lista.append(st.selectbox('Selecione o turno', turnos ))
	lista.append(st.selectbox('Selecione o departamento', departamentos))
	lista.append(st.selectbox('Selecione a linha', linhas))
	lista.append(st.selectbox('Selecione o equipamento', equipamentos))
	lista.append(st.selectbox('Selecione o gatilho', gatilhos))
	lista.append(st.text_input('Descreva a anomalia', ""))
	lista.append(st.text_input('Ordem de manutenção', ""))
	lista.append(st.text_input('Descreva a correção', ""))
	lista.append(st.text_input('1) Por que?', ""))
	lista.append(st.text_input('2) Por que?', ""))
	lista.append(st.text_input('3) Por que?', ""))
	lista.append(st.text_input('4) Por que?', ""))
	lista.append(st.text_input('5) Por que?', ""))
	lista.append(st.multiselect('Selecione o tipo da falha', falhas))
	lista.append(st.multiselect('Selecione o tipo da deterioização (falha)', deterioização))
	lista.append(st.multiselect('Selecione o tipo da correção', falhas))
	lista.append(st.multiselect('Selecione o tipo da deterioização (correção)', deterioização))
	lista.append(st.text_input('Ações tomadas', ""))
	lista.append(st.text_input('Notas de manutenção', ""))
	lista.append(st.text_input('Responsável pela identificação da anomalia', ""))
	lista.append(st.text_input('Responsável pela correção da anomalia', ""))
	submitted1 = st.form_submit_button('Enviar 5 Porquês')
	'''

