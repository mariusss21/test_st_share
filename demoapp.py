######################################################################################################
                                           #Introdução
######################################################################################################
# O sistema desenvolvido coleta os dados dos 5 porques através de um formulário web e armazena num  
# banco no-SQL. Esses dados são ligos e disponibilizados para visualização e edição

# Tecnologias:
# Streamlit para web, streamlit share para deploy, banco de dados Firebase (Google)

# Link:
# https://share.streamlit.io/mariusss21/test_st_share/main/demoapp.py
######################################################################################################
                                 # importar bibliotecas
######################################################################################################

import streamlit as st
from streamlit_tags import st_tags
from streamlit import caching
import plotly.express as px
import pandas as pd
#import numpy as np
import json
import smtplib
import time
import base64

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
inserir = st.sidebar.checkbox("Inserir ocorrência 5 Porquês")
analisar = st.sidebar.checkbox("Avaliar ocorrência 5 Porquês")
estatistica = st.sidebar.checkbox("Estatísticas de ocorrências")

######################################################################################################
                                           #Função para enviar email
######################################################################################################
# Recebe como parâmetros destinatário e um código de atividade para o envio
# O email está configurado por parâmetros presentes no streamlit share (secrets)
def send_email(to, atividade, documento, comentario):
	gmail_user = st.secrets["email"]
	gmail_password = st.secrets["senha"]
	sent_from = gmail_user
	from_ = 'Ambev 5 Porques'
	subject = ""
	body = ''
	atividade = int(atividade)
	
	if atividade == 0:
		body = "Ola, foi gerada um novo 5-Porques, acesse a plataforma para avaliar.\nhttps://share.streamlit.io/mariusss21/test_st_share/main/demoapp.py\n\nAtenciosamente, \nAmbev 5-Porques"
		subject = """Gerado 5-Porques %s""" % (documento)
	elif atividade == 1:
		body = "Ola, o responsavel retificou 5-Porques, acesse a plataforma para reavaliar.\nhttps://share.streamlit.io/mariusss21/test_st_share/main/demoapp.py\n\nAtenciosamente, \nAmbev 5-Porques"
		subject = """Retificado 5-Porques %s""" % (documento)
	elif atividade == 2:
		body = """Ola, o gestor aprovou 5-Porques.\n\n%s \n\nAtenciosamente, \nAmbev 5-Porques""" %(comentario)
		subject = """Aprovado 5-Porques %s""" % (documento)	
	elif atividade == 3:
		body = """Ola, o gestor reprovou 5-Porques, acesse a plataforma para retificar.\nhttps://share.streamlit.io/mariusss21/test_st_share/main/demoapp.py \n\n Comentario do gestor: \n\n%s  \n\nAtenciosamente, \nAmbev 5-Porques""" %(comentario)
		subject = """Reprovado 5-Porques %s""" % (documento)		
	
	email_text = """From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (from_, to, subject, body)
	#email_text.set_charset('utf8')
	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, email_text.encode('latin-1'))
		server.close()
		st.write('E-mail enviado!')
	except:
		st.error('Falha ao enviar e-mail, tente novamente')

######################################################################################################
                                           #Função para download
######################################################################################################
		
def download(df):
	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	in:  dataframe
	out: href string
	"""
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
	href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
	return href

######################################################################################################
                                           #Função para leitura do banco (Firebase)
######################################################################################################
# Efetua a leitura de todos os documentos presentes no banco e passa para um dataframe pandas
# Função para carregar os dados do firebase (utiliza cache para agilizar a aplicação)
@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	posts_ref = db.collection("5porques_2")	
	for doc in posts_ref.stream():
		dicionario = doc.to_dict()
		dicionario['document'] = doc.id
		data = data.append(dicionario, ignore_index=True)

	data['data'] = pd.to_datetime(data['data']).dt.date
	return data

# Efetua a leitura dos dados dos usuários no banco
@st.cache
def load_usuarios():
	data = pd.DataFrame(columns=['Nome', 'Email', 'Gestor', 'Codigo'])
	posts_ref = db.collection("Usuarios")	
	for doc in posts_ref.stream():
		dicionario = doc.to_dict()
		dicionario['document'] = doc.id
		data = data.append(dicionario, ignore_index=True)
	return data

# Efetua a leitura dos dados das linhas e dos equipamentos
@st.cache
def load_sap_nv3():
	data = pd.read_csv('SAP_nivel3.csv', sep=';')
	return data
			   
######################################################################################################
                                           #Avaliação e edição das ocorrências
######################################################################################################
# Função para aprovar ou reprovar a ocorrência. Permite também a edição de ocorrências passadas,
# possibilitando a retificação das mesmas. Edição através de formulário que aparece preenchido com
# os valores passados anteriormente

def func_validar(index, row, indice):

	if row['document'] in indice:
		editar = st.checkbox('Editar 5-Porques ' + str(row['document']))
		
		if not editar:
			st.table(row)
			st.subheader('Avaliação do 5-Porques')
			comentario = st.text_input('Envie um comentário sobre 5-Porques' + ' (' + str(index) + '):',"")			
			bt1, bt2 = st.beta_columns(2)
			aprovar = bt1.button('Aprovar 5-Porques ' + '(' + str(index) + ')')
			reprovar = bt2.button('Reprovar 5-Porques ' + '(' + str(index) + ')')
			st.subheader('Exportar 5-Porques')
			#down1, down2 = st.beta_columns(2)
			#down_pdf = down1.button('Download 5-Porques em pdf' + ' (' + str(index) + ')')
			#down_excel = down2.button('Download 5-Porques em excel' + ' (' + str(index) + ')')
			
			st.markdown(download(row), unsafe_allow_html=True)
			#if down_excel:
			#	download(row)

			if aprovar:
				caching.clear_cache()
				att_verificado = {}
				att_verificado['status'] = 'Aprovado'
				db.collection("5porques_2").document(row['document']).update(att_verificado)
				send_email(row['email responsável'], 2, str(row['document']), comentario)
				#caching.clear_cache()

			if reprovar:
				if comentario == '':
					st.error('Obrigatório o preenchimento do comentário!')
				else:
					caching.clear_cache()
					att_verificado = {}
					att_verificado['status'] = 'Reprovado'
					db.collection("5porques_2").document(row['document']).update(att_verificado)
					send_email(row['email responsável'], 3, str(row['document']), comentario)
					#caching.clear_cache()
		else:
			documento = str(row['document'])	
			doc = row.to_dict()
			
			list_linhas = list(linhas)
			sap_nv2 = st.selectbox('Selecione a linha' + ' (' + str(index) + '):', list_linhas, list_linhas.index(doc['linha']))
			equipamentos = list(sap_nv3[sap_nv3['Linha'] == sap_nv2]['equipamento'])
			
			if sap_nv2 != doc['linha']:
				equipamento_ant = 0
			else:
				equipamento_ant = equipamentos.index(doc['equipamento'])
			
			with st.form('Form_edit' + str(index)):
				dic['data'] = st.date_input('Data da ocorrência' + ' (' + str(index) + '):', doc['data'])
				dic['turno'] = st.selectbox('Selecione o turno' + ' (' + str(index) + '):', turnos, turnos.index(doc['turno']) )
				dic['departamento'] = st.selectbox('Selecione o departamento' + ' (' + str(index) + '):', departamentos, departamentos.index(doc['departamento']))
				dic['linha'] = sap_nv2
				dic['equipamento'] = st.selectbox('Selecione o equipamento' + ' (' + str(index) + '):', equipamentos, equipamento_ant)
				dic['gatilho'] = st.selectbox('Selecione o gatilho' + ' (' + str(index) + '):', gatilhos, gatilhos.index(doc['gatilho']))
				dic['descrição anomalia'] = st.text_input('Descreva a anomalia' + ' (' + str(index) + '):', value=doc['descrição anomalia'])
				dic['ordem manutenção'] = st_tags(label=('Ordem de manutenção' + ' (' + str(index) + '):'), text='Pressione enter', value=doc['ordem manutenção'].replace(']', '').replace('[','').replace("'",'').split(','))
				dic['correção'] = st.text_input('Descreva a correção' + ' (' + str(index) + '):', value=doc['correção'])
				dic['pq1'] = st.text_input('1) Por que?' + ' (' + str(index) + '):', value=doc['pq1'])
				dic['pq2'] = st.text_input('2) Por que?' + ' (' + str(index) + '):', value=doc['pq2'])
				dic['pq3'] = st.text_input('3) Por que?' + ' (' + str(index) + '):', value=doc['pq3'])
				dic['pq4'] = st.text_input('4) Por que?' + ' (' + str(index) + '):', value=doc['pq4'])
				dic['pq5'] = st.text_input('5) Por que?' + ' (' + str(index) + '):', value=doc['pq5'])
				dic['tipo de falha'] = st.multiselect('Selecione o tipo da falha' + ' (' + str(index) + '):', falhas)
				dic['falha deterioização'] = st.multiselect('Selecione o tipo da deterioização (falha)' + ' (' + str(index) + '):', deterioização)
				dic['tipo de correção'] = st.multiselect('Selecione o tipo da correção' + ' (' + str(index) + '):', falhas)
				dic['correção deterioização'] = st.multiselect('Selecione o tipo da deterioização (correção)' + ' (' + str(index) + '):', deterioização)
				dic['ações'] = st.text_input('Ações' + ' (' + str(index) + '):', value=doc['ações'])
				dic['notas de manutenção'] = st_tags(label=('Notas de manutenção' + ' (' + str(index) + '):'), text='Pressione enter', value=doc['notas de manutenção'].replace(']', '').replace('[','').replace("'",'').split(','))
				dic['responsável identificação'] = st.text_input('Responsável pela identificação' + ' (' + str(index) + '):', value=doc['responsável identificação'])
				dic['responsável reparo'] = st.text_input('Responsável pela correção' + ' (' + str(index) + '):',value=doc['responsável reparo'])
				dic['email responsável'] = st.text_input('E-mail do responsável pelo formulário' + ' (' + str(index) + '):', value=doc['email responsável'])
				dic['gestor'] = st.selectbox('Coordenador' + ' (' + str(index) + '):', gestores, gestores.index(doc['gestor']))
				dic['status'] = 'Retificado'
				submitted_edit = st.form_submit_button('Editar 5 Porquês' + ' (' + str(index) + '):')

			if submitted_edit:
				keys_values = dic.items()
				new_d = {str(key): str(value) for key, value in keys_values}
				for key, value in new_d.items():
					if (value == '') or value == '[]':
						new_d[key] = 'Não informado'
				if '@ambev.com.br' in new_d['email responsável']:
					db.collection("5porques_2").document(documento).set(new_d,merge=True)
					editar = False
					send_email(usuarios_fb[usuarios_fb['Nome'] == new_d['gestor']]['Email'], 1, documento, '')
					caching.clear_cache()
				else:
					st.error('Por favor inserir e-mail Ambev válido')
					
######################################################################################################
                                           #Formulário para inclusão de ocorrência
######################################################################################################

def formulario(linhas):
	sp2, sp3, st0 = st.beta_columns(3)
	list_linhas = list(linhas)
	sap_nv2 = sp2.selectbox('Selecione a linha', list_linhas)	
	equipamentos = list(sap_nv3[sap_nv3['Linha'] == sap_nv2]['equipamento'])

	with st.form('Form_ins'):
		st1, st2, st3 = st.beta_columns(3)
		dic['data'] = st1.date_input('Data da ocorrência')
		dic['turno'] = st2.selectbox('Selecione o turno', turnos )
		dic['departamento'] = st3.selectbox('Selecione o departamento', departamentos)
		dic['linha'] = sap_nv2
		dic['equipamento'] = sp3.selectbox('Selecione o equipamento', equipamentos)
		dic['gatilho'] = st0.selectbox('Selecione o gatilho', gatilhos)		
		dic['descrição anomalia'] = st.text_input('Descreva a anomalia', "")
		st4, st5 = st.beta_columns(2)
		dic['correção'] = st.text_input('Descreva a correção', "")
		st6, st7 = st.beta_columns(2)
		dic['pq1'] = st.text_input('1) Por que?', "")
		dic['pq2'] = st.text_input('2) Por que?', "")
		dic['pq3'] = st.text_input('3) Por que?', "")
		dic['pq4'] = st.text_input('4) Por que?', "")
		dic['pq5'] = st.text_input('5) Por que?', "")
		dic['tipo de falha'] = st4.multiselect('Selecione o tipo da falha', falhas)
		dic['falha deterioização'] = st5.multiselect('Selecione o tipo da deterioização (falha)', deterioização)
		dic['tipo de correção'] = st6.multiselect('Selecione o tipo da correção', falhas)
		dic['correção deterioização'] = st7.multiselect('Selecione o tipo da deterioização (correção)', deterioização)
		dic['ações'] = st.text_input('Ações', "")
		st8, st9 = st.beta_columns(2)
		dic['responsável identificação'] = st8.text_input('Responsável pela identificação')
		dic['responsável reparo'] = st9.text_input('Responsável pela correção')
		dic['email responsável'] = st.text_input('E-mail do responsável pelo formulário')
		dic['gestor'] = st.selectbox('Coordenador', gestores)
		dic['notas de manutenção'] = st_tags(label='Notas de manutenção', text='Pressione enter')
		dic['ordem manutenção'] = st_tags(label='Ordens de manutenção', text='Pressione enter')
		dic['status'] = 'Pendente'
		submitted_ins = st.form_submit_button('Enviar 5 Porquês')

	if submitted_ins:
		caching.clear_cache()
		keys_values = dic.items()
		new_d = {str(key): str(value) for key, value in keys_values}
		for key, value in new_d.items():
			if (value == '') or value == '[]':
				new_d[key] = 'Não informado'
				
		if '@ambev.com.br' in new_d['email responsável']:
			ts = time.time()
			val_documento = new_d['linha'] + '-' + new_d['equipamento'].replace(" ", "") + '-' + str(int(ts))
			doc_ref = db.collection("5porques_2").document(val_documento)
			doc_ref.set(new_d)
			send_email(usuarios_fb[usuarios_fb['Nome'] == new_d['gestor']]['Email'], 0, val_documento, '')
		else:
			st.error('Por favor inserir e-mail Ambev válido')
		
######################################################################################################
                                           #Main
######################################################################################################

# Carrega dataframe e extrai suas colunas
dados = load_data()
usuarios_fb = load_usuarios()
sap_nv3 = load_sap_nv3()
gestores = list(usuarios_fb[usuarios_fb['Gestor'].str.lower() == 'sim']['Nome'])
nao_gestores = list(usuarios_fb[usuarios_fb['Gestor'].str.lower() != 'sim']['Nome'])
colunas = dados.columns

# Constantes
equipamentos = []
gatilhos = [ 'Segurança', '10 minutos', '30 minutos', '1 hora']
linhas = sap_nv3['Linha'].drop_duplicates()
turnos = ['Turno A', 'Turno B', 'Turno C']
departamentos = ['Engenharia', 'Automação', 'Manutenção']
falhas = ['Máquina', 'Mão-de-obra', 'Método', 'Materiais', 'Meio ambiente', 'Medição', 'Outra']
deterioização = ['Forçada', 'Natural', 'Nenhuma']

# Imagem
st.image('Ambev.jpeg')
st.subheader('Aplicação 5-porques')
st.write('Selecione no menu lateral a opção desejada')

# Lista vazia para input dos dados do formulário
dic = {} #dicionario

if inserir:
	st.subheader('Formulário 5-porques')
	formulario(linhas)

if analisar:
	st.subheader('Configure as opções de filtro')
	st.text('Selecione a data')
	col1, col2 = st.beta_columns(2)
	inicio_filtro = col1.date_input("Início")
	fim_filtro = col2.date_input("Fim")
	filtrado = (dados[(dados['data'] >= inicio_filtro) & (dados['data'] <= fim_filtro)]) 
	
	list_resp = list(filtrado['responsável identificação'].drop_duplicates())
	list_resp.append('todos') 
	responsavel = st.selectbox("Selecione o responsável", list_resp, list_resp.index('todos'))
	if responsavel == 'todos':
		pass
	elif responsavel is not None and (str(responsavel) != 'nan'):
		filtrado = filtrado[filtrado['responsável identificação'] == responsavel]
		
	list_gestor = list(filtrado['gestor'].drop_duplicates())
	list_gestor.append('todos')  
	gestor = st.selectbox("Selecione o gestor", list_gestor, list_gestor.index('todos'))
	if gestor == 'todos':
		pass
	elif gestor is not None and (str(gestor) != 'nan'):
		filtrado = filtrado[filtrado['gestor'] == gestor]	
	
	list_status = list(filtrado['status'].drop_duplicates())
	list_status.append('todos') 
	status = st.selectbox("Selecione o status", list_status, list_status.index('todos'))
	if status == 'todos':
		pass
	elif status is not None and (str(status) != 'nan'):
		filtrado = filtrado[filtrado['status'] == status]	
	
	st.write(filtrado[['data', 'document', 'gestor', 'status','responsável identificação', 'turno', 'linha', 'equipamento']])
	indice_doc = st.multiselect('Selecione a ocorrência', filtrado['document'].tolist())
	for index, row in filtrado.iterrows():
		if row['document'] in indice_doc:
			st.subheader('Ocorrência ' + str(row['document']))
			func_validar(index, row, indice_doc)
			        
if estatistica:
	st.subheader("Estatísticas das ocorrências")
	variavel =  st.selectbox('Selecione o item para análise', colunas)
	fig = px.histogram(dados, x=variavel)
	st.write(fig)
	
