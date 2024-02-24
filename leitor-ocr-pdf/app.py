import pandas as pd
import openpyxl
import psycopg2
import os
import tempfile
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import time
from flask import Flask, request, render_template,redirect
from werkzeug.utils import secure_filename
import shutil
from werkzeug.datastructures import FileStorage
from threading import Thread
from multiprocessing import Process

#database connection
##########################################################################################################################################################
app = Flask(__name__)
load_dotenv()

db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

arquivos = []

try:
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    cursor = conn.cursor()

except psycopg2.Error as e:
    print("Erro ao conectar ao banco de dados:", e)

##########################################################################################################################################################

#functions
##########################################################################################################################################################
def search_path():
    global arquivos
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".xlsx") or file.endswith(".xls"):
                arquivos.append(os.path.join(root, file))
                print (arquivos)

def open_file():
    for arquivo in arquivos:
        try:
            print("entrou")
            planilha = pd.read_excel(arquivo)
            result = extract_columns(planilha)
            result = dataframe_to_list_of_dicts(result)
            insert_data_to_database(result)
            print("finalizou")
        except ValueError as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")

def extract_columns(planilha):
    def format_dates(df):
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':  # Verifica se é uma coluna de data
                df[col] = df[col].dt.strftime('%Y-%m-%d')  # Converte a data para o formato 'YYYY-MM-DD'
        return df
    
    def remove_special_characters(cpf):
        return cpf.replace('.', '').replace('-', '')  
    
    def remove_extra_spaces(text):
        if isinstance(text, str):
            return ' '.join(text.split())
        else:
            return text
        
    if planilha is not None:
        colunas_especificas = [
            "ContratoId",
            "NumeroProposta",
            "UsuarioDigitacaoBanco",
            "DataInclusao",
            "CpfCliente",
            "Banco",
            "Convenio",
            "Prazo",
            "ValorBruto",
            "ValorLiquido",
            "ValorParcela",
            "ValorBase",
            "ComissaoEmpresaVistaValor",
            "ComissaoRepasseValor",
            "NomeCorretor",
            "StatusBancoEmpresa",
            "DataStatusBancoEmpresa",
            "SubStatusBancoEmpresa",
            "StatusBancoCliente"
        ]
        
        colunas_extraidas = planilha.loc[:, colunas_especificas]
        
        colunas_extraidas = colunas_extraidas.fillna("null value")
        
        # Chama a função interna para formatar as datas
        colunas_extraidas = format_dates(colunas_extraidas)
        
        # Chama a função interna para remover os caracteres especiais do CPF
        colunas_extraidas['CpfCliente'] = colunas_extraidas['CpfCliente'].apply(remove_special_characters)

        colunas_extraidas['StatusBancoCliente'] = colunas_extraidas['StatusBancoCliente'].apply(remove_extra_spaces)

        return colunas_extraidas
    else:
        return "Fail"

def get_current_timestamp():
    unix_timestamp = int(time.time())

    return unix_timestamp

def dataframe_to_list_of_dicts(df):
    return df.to_dict(orient='records')

def insert_data_to_database(data):
    if data != "Fail":

        timestamp = get_current_timestamp()
        flag=0
        total_rows = len(data)
        rows_processed = 0
        commit_interval = 100

        while rows_processed < total_rows:
            data_batch = data[rows_processed:rows_processed+commit_interval]
            rows_processed += commit_interval

            for row in data_batch:
                row['upload_id'] = timestamp
    
                values = list(row.values())
                cursor.execute(
                    "INSERT INTO upload_proposal_2tech (contrato_id, numero_proposta, usuario_digitacao_banco, data_inclucao, cpf_cliente, banco, convenio, prazo, valor_bruto, valor_liquido, valor_parcela, valor_base, comissao_empresa_vista_valor, comissao_repasse_valor, nome_corretor, status_banco_empresa, data_status_banco_empresa, sub_status_banco_empresa, status_banco_cliente , upload_id) VALUES (%s, %s, %s, TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,TO_DATE(%s, 'DD-MM-YYYY'), %s, %s, %s)",
                    values)

            conn.commit()
            print(f"Commit parcial de {commit_interval} dados inseridos com sucesso.")

        print(f"Total de {total_rows} dados inseridos com sucesso.")
    else:
        print("Falha ao extrair dados.")

def limpar_pasta(diretorio):
    # Verifica se o diretório existe
    if not os.path.exists(diretorio):
        print(f'Diretório "{diretorio}" não encontrado.')
        return
    
    # Itera sobre todos os arquivos e subpastas dentro do diretório
    for nome_arquivo in os.listdir(diretorio):
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        
        # Verifica se o caminho é um arquivo (não é uma pasta)
        if os.path.isfile(caminho_arquivo):
            # Remove o arquivo
            os.remove(caminho_arquivo)
        else:
            # Se for uma pasta, remove recursivamente todos os arquivos e subpastas dentro dela
            shutil.rmtree(caminho_arquivo)


##########################################################################################################################################################

#flask
        
@app.route('/Huginn', methods=["GET","POST"])
def huginn_route():
    return render_template('index.html',variavel="teste")

def background_open_file():
    search_path()
    open_file()

@app.route('/upload', methods=['POST'])
def upload_files():
    limpar_pasta('temp')

    flag = 1
    uploaded_files = request.files.getlist('files[]')
    print(str(uploaded_files))
    if len(uploaded_files) != 0 and str(uploaded_files) != "[<FileStorage: '' ('application/octet-stream')>]":

        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        for uploaded_file in uploaded_files:
            filename = uploaded_file.filename
            if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
                resposta = "Apenas arquivos nos formatos .xlsx e .xls são aceitos. Por favor, selecione um arquivo válido e tente novamente"
                return render_template('index3.html', message=resposta)
            else:
                temp_file_path = os.path.join(temp_dir, filename)
                uploaded_file.save(temp_file_path)

                p = Process(target=background_open_file)
                p.start()

        return render_template('index2.html', message="Tudo Certo! Recebemos seus arquivos.")
    else:
        print(str(uploaded_files))
        message = "Selecione pelo menos um arquivo antes de enviar"
        return render_template('index3.html', message=message)
    
@app.route('/doc')
def documentation():
    return render_template()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)