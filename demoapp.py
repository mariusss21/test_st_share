# importar bibliotecas
import streamlit as st
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

#Leitura dos dados, cache temporariamente desabilitado por conta da nserção de novos valores
@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	return data

# Carrega dataframe e extrai suas colunas
df_col = load_data()
colunas = df_col.columns

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

# Etapa de login
#login = False

#if not logado:
#	with st.sidebar.form('senha'):
#		senha = st.text_input('Digite a senha para acesso', "")
#		login = st.form_submit_button('Login')
#	if login:
#		if senha == st.secrets['senha_con']:
#			st.write('Login efetuado com sucesso')
#			logado = True
#		else:
#			st.write('Senha incorreta')
#			logado = False

#if logado:
#	logoff = st.button('Logoff')
#	if logoff:
#		logado = False

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
	
	# And then uploading some data to that reference
	#doc_ref.set({
	#"title": "Apple",
	#"url": "www.apple.com"
	#})
	# Now let's make a reference to ALL of the posts



		
leitura = st.button('Ler dados da Nuvem')

if leitura:
	# Informa a coleção para leitura
	posts_ref = db.collection("5porques_2")
	
	# For a reference to a collection, we use .stream() instead of .get()
	for doc in posts_ref.stream():
		#st.write("The id is: ", doc.id)
		#st.write("The contents are: ", doc.to_dict())
		df = df.append(doc.to_dict(), ignore_index=True, columns=colunas)
		#st.write(type(doc))
	st.write(df.head())
	df['data'] = pd.to_datetime(df['data']).dt.date
		
st.subheader('Selecione a data de início e fim para filtrar as cocorrências')
	 
col1, col2 = st.beta_columns(2)

#col1.header("Início")
inicio_filtro = col1.date_input("Início")

#col2.header("Fim")
fim_filtro = col2.date_input("Fim")
	 
filtrar = st.button('Filtrar ocorrências')

if filtrar:
	st.write(inicio_filtro)
	st.write(fim_filtro)
	
st.write(df[(df['data'] >= inicio_filtro) & (df['data'] <= fim_filtro)])
st.write(df)
# referencias 
# https://blog.streamlit.io/secrets-in-sharing-apps/
# https://blog.streamlit.io/streamlit-firestore/
# https://blog.streamlit.io/streamlit-firestore-continued/

	#df2 = pd.DataFrame(lista).T
	#df2.columns = colunas
	#st.write(df2.head())
	#df2.astype('category')
	#dados = df2.to_dict()
		#st.write(df2.pivot(columns=colunas))
	
	#df = pd.concat([df, df2], join='inner', ignore_index=True)
	#df.to_csv(DATA_URL, index=False)
	# This time, we're creating a NEW post reference for Apple
