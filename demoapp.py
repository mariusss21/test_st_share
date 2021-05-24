######################################################################################################
                                 # importar bibliotecas
######################################################################################################

import streamlit as st
from streamlit import caching
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import smtplib

from google.cloud import firestore
from google.oauth2 import service_account

######################################################################################################
				#Configurando acesso ao firebase
######################################################################################################

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="streamlit-cb45e")
doc_ref = db.collection(u'5porques')

# Link do arquivo com os dados
DATA_URL = "data.csv"

######################################################################################################
				     #Definição da sidebar
######################################################################################################


st.sidebar.title("Escolha a ação desejada")
inserir = st.sidebar.checkbox("Inserir ocorrência 5 Porquês", value=True)
analisar = st.sidebar.checkbox("Avaliar ocorrência 5 Porquês")
estatistica = st.sidebar.checkbox("Estatísticas de ocorrências")

######################################################################################################
                                           #Funções
######################################################################################################

#função para carregar os dados do firebase (utiliza cache para agilizar a aplicação)
@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	posts_ref = db.collection("5porques_2")	
	# For a reference to a collection, we use .stream() instead of .get()
	for doc in posts_ref.stream():
		dicionario = doc.to_dict()
		dicionario['document'] = doc.id
		data = data.append(dicionario, ignore_index=True)

	data['data'] = pd.to_datetime(data['data']).dt.date
	data = data.sort_values(by=['data'])
	data.reset_index(inplace = True)
	return data

def func_validar(index, row, indice):
	if index in indice:
		st.table(row)
		
		bt1, bt2, bt3 = st.beta_columns(3)
		aprovar = bt1.button('Aprovar')
		reprovar = bt2.button('Reprovar')
		editar = bt3.button('Editar')
		
		if aprovar:
			caching.clear_cache()
			att_verificado = {}
			att_verificado['status'] = 'Aprovado'
			db.collection("5porques_2").document(row['document']).update(att_verificado)
			caching.clear_cache()
		
		if reprovar:
			caching.clear_cache()
			att_verificado = {}
			att_verificado['status'] = 'Reprovado'
			db.collection("5porques_2").document(row['document']).update(att_verificado)
			caching.clear_cache()
			
		if editar:
			editar_registro(str(row['document']))			

# email
def send_email():
	gmail_user = st.secrets["email"]
	gmail_password = st.secrets["senha"]
	sent_from = gmail_user
	from_ = 'Ambev 5 Porques'
	to = 'marius.lisboa@gmail.com'
	subject = "Nova ocorrencia gerada"
	body = "Ola, foi gerada uma nova ocorrencia, acesse a plataforma para avalia-la. \nAtenciosamente, \nAmbev 5 Porques"
	email_text = """From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (from_, to, subject, body)

	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, email_text)
		server.close()
		st.write('Email sent!')
	except:
		st.write('Whoops, something went wrong...')
		
#função formulário 
def formulario():
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
		dic['gestor'] = st.text_input('Gestor responsável pela avaliação da ocorrência', "")
		dic['status'] = 'Pendente'
		submitted1 = st.form_submit_button('Enviar 5 Porquês')

	if submitted1:
		caching.clear_cache()
		keys_values = dic.items()
		new_d = {str(key): str(value) for key, value in keys_values}
		doc_ref = db.collection("5porques_2").document()
		doc_ref.set(new_d)
		
		
def editar_registro(documento):

	doc = db.collection("posts").document(documento).get()	    		    				   
	with st.form('Form1'):
		dic['data'] = st.date_input('Data da ocorrência', value=doc['data'])
		dic['turno'] = st.selectbox('Selecione o turno', turnos )
		dic['departamento'] = st.selectbox('Selecione o departamento', departamentos)
		dic['linha'] = st.selectbox('Selecione a linha', linhas)
		dic['equipamento'] = st.selectbox('Selecione o equipamento', equipamentos)
		dic['gatilho'] = st.selectbox('Selecione o gatilho', gatilhos)
		dic['descrição anomalia'] = st.text_input('Descreva a anomalia', "", value=doc['descrição anomalia'])
		dic['ordem manutenção'] = st.text_input('Ordem de manutenção', "", value=doc['ordem manutenção'])
		dic['correção'] = st.text_input('Descreva a correção', "", value=doc['correção'])
		dic['pq1'] = st.text_input('1) Por que?', "", value=doc['pq1'])
		dic['pq2'] = st.text_input('2) Por que?', "", value=doc['pq2'])
		dic['pq3'] = st.text_input('3) Por que?', "", value=doc['pq3'])
		dic['pq4'] = st.text_input('4) Por que?', "", value=doc['pq4'])
		dic['pq5'] = st.text_input('5) Por que?', "", value=doc['pq5'])
		dic['tipo de falha'] = st.multiselect('Selecione o tipo da falha', falhas)
		dic['falha deterioização'] = st.multiselect('Selecione o tipo da deterioização (falha)', deterioização)
		dic['tipo de correção'] = st.multiselect('Selecione o tipo da correção', falhas)
		dic['correção deterioização'] = st.multiselect('Selecione o tipo da deterioização (correção)', deterioização)
		dic['ações'] = st.text_input('Ações tomadas', "", value=doc['ações'])
		dic['notas de manutenção'] = st.text_input('Notas de manutenção', "", value=doc['notas de manutenção'])
		dic['responsável identificação'] = st.text_input('Responsável pela identificação da anomalia', "", value=doc['responsável identificação'])
		dic['responsável reparo'] = st.text_input('Responsável pela correção da anomalia', "", value=doc['responsável reparo'])
		dic['gestor'] = st.text_input('Gestor responsável pela avaliação da ocorrência', "")
		dic['status'] = 'Retificado'
		submitted1 = st.form_submit_button('Enviar 5 Porquês')

	if submitted1:
		caching.clear_cache()
		keys_values = dic.items()
		new_d = {str(key): str(value) for key, value in keys_values}
		doc_ref = db.collection("5porques_2").document(documento)
		doc_ref.set(new_d)


######################################################################################################
                                           #Main
######################################################################################################

# Carrega dataframe e extrai suas colunas
dados = load_data()
colunas = dados.columns

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

teste_email = st.button('Teste email')
if teste_email:
	pass
	#send_email()

# Lista vazia para input dos dados do formulário
dic = {} #dicionario
submitted1=False

if inserir:
	st.subheader('Formulário para incluir ocorrência')
	formulario()

if analisar:
	st.subheader('Configure as opções de filtro')
	st.text('Selecione a data')
	col1, col2 = st.beta_columns(2)
	inicio_filtro = col1.date_input("Início")
	fim_filtro = col2.date_input("Fim")
	filtrado = (dados[(dados['data'] >= inicio_filtro) & (dados['data'] <= fim_filtro)]) 
		
	#st.text('Selecione o responsável pelo preenchimento do formulário')
	responsavel = st.selectbox("Selecione o responsável", list(filtrado['responsável identificação'].drop_duplicates()))	
	if responsavel is not None and (str(responsavel) != 'nan'):
		filtrado = filtrado[filtrado['responsável identificação'] == responsavel]
		
	#st.text('Selecione o Gestor')
	gestor = st.selectbox("Selecione o gestor", list(filtrado['gestor'].drop_duplicates()))
	if gestor is not None and (str(gestor) != 'nan'):
		filtrado = filtrado[filtrado['gestor'] == gestor]	
	
	#st.text('Selecione o status da ocorrência')
	status = st.selectbox("Selecione o status", list(filtrado['status'].drop_duplicates()))
	if status is not None and (str(status) != 'nan'):
		filtrado = filtrado[filtrado['status'] == status]	
	
	st.write(filtrado[['data', 'responsável identificação', 'gestor', 'status', 'turno', 'linha', 'equipamento']])
	detalhar_todas = st.checkbox("Detalhar todas as ocorrências")
	
	if not detalhar_todas:
		indice = st.multiselect('Selecione a ocorrência', filtrado.index)

	for index, row in filtrado.iterrows():
		if detalhar_todas:
			st.subheader('Ocorrência ' + str(index))
			st.table(row)
		else:
			if index in indice:
			       st.subheader('Ocorrência ' + str(index))
			       func_validar(index, row, indice)
			        
if estatistica:
	st.subheader("Estatísticas das ocorrências")
	fig = plt.figure()
	variavel =  st.selectbox('Selecione o item para análise', colunas)
	ax = fig.add_subplot(1,1,1)
	plt.xticks(rotation=45)
	ax.hist(dados[variavel])
	st.write(fig)
