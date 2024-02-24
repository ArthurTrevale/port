import configparser
import os

# Função para verificar e criar o arquivo settings.txt se não existir
def verificar_arquivo_settings():
    if not os.path.exists('settings.txt'):
        config = configparser.ConfigParser()
        config['Configuracoes'] = {
            'User': '',
            'Password': '',
            'Url':'',
            'Url2':'',
            'Url3':'',
            'Time':'15',
            'Theme':'True',
            'Clogin':'',
            'Cpassword':'',
            'Captcha':''
        }
        
        with open('settings.txt', 'w') as config_file:
            config.write(config_file)

# Função para obter o valor de um campo do arquivo settings.txt
def get(campo):
    config = configparser.ConfigParser()
    config.read('settings.txt')
    return config['Configuracoes'][campo]

# Função para definir um novo valor para um campo no arquivo settings.txt
def set(campo, novo_valor):
    config = configparser.ConfigParser()
    config.read('settings.txt')

    if 'Configuracoes' not in config:
        config.add_section('Configuracoes')

    if campo in config['Configuracoes']:
        config['Configuracoes'][campo] = novo_valor
        with open('settings.txt', 'w') as config_file:
            config.write(config_file)
        return f'Key {campo} is modifiqued'
    else:
        return f"Key '{campo}' not found"

#cria nova chave
def new(chave, valor):
    config = configparser.ConfigParser()
    config.read('settings.txt')

    # Adiciona a nova chave ao dicionário Configuracoes
    config['Configuracoes'][chave] = valor

    # Salva as alterações no arquivo
    with open('settings.txt', 'w') as config_file:
        config.write(config_file)

def delete_key(chave):
    config = configparser.ConfigParser()
    config.read('settings.txt')

    if 'Configuracoes' in config and chave in config['Configuracoes']:
        del config['Configuracoes'][chave]
        with open('settings.txt', 'w') as config_file:
            config.write(config_file)
        return f'Key {chave} and its value are deleted'
    else:
        return f"Key '{chave}' not found"

def get_all():
    config = configparser.ConfigParser()
    config.read('settings.txt')

    # Obtém todas as chaves e valores do dicionário Configuracoes
    keys_and_values = config['Configuracoes'].items()

    # Formata os dados como uma lista de dicionários
    result_list = [{'key': key, 'value': value} for key, value in keys_and_values]

    return result_list

def get_help(flag):
    if flag == 1:
        config_file='help2.txt'
        try:
            with open(config_file, 'r', encoding='latin-1') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Erro ao ler o arquivo de ajuda: {e}"
    else:
        config_file='help.txt'
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Erro ao ler o arquivo de ajuda: {e}"

def verificar_arquivo_help(nome_arquivo, conteudo):
    if not os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'w') as arquivo:
            arquivo.write(conteudo)

# Conteúdo para help.txt
conteudo_help = """
get infos
Description Retrieves all key-value pairs from the configuration

set infos
Open a new window to inject the information

set info
Description Sets a new value for a given key in the configuration
Usage set info key value
Example "set info username JohnDoe"

get info
Description Retrieves the value of a specific key from the configuration
Usage get info [key]
Example "get info username"

new info
Description Creates a new key-value pair in the configuration
Usage new info [key] [value]
Example "new info email john@example.com"

del info
Description Deletes a key and its associated value from the configuration
Usage del info [key]
Example "del info email"

set color
Description Sets the text color for the console or input prompt
Usage set color [console/input] [color]
Example "set color console blue"

open
Description Opens a file with the default application
Usage open [file_path]
Example "open C:/Documents/example.txt"

run/start
Description Executes start the bot

finish/stop
Description Closes the application window

change theme
Description Toggles between dark and light themes
Usage change theme

clear
usage to clear all texts and logs in terminal 
"""

# Conteúdo para help2.txt
conteudo_help2 = """
get infos
Descrição: Recupera todos os pares chave-valor da configuração

set info
Descrição: Define um novo valor para uma chave específica na configuração
Uso: set info chave valor
Exemplo: "set info usuario JoaoDoe"

get info
Descrição: Recupera o valor de uma chave específica na configuração
Uso: get info [chave]
Exemplo: "get info usuario"

new info
Descrição: Cria um novo par chave-valor na configuração
Uso: new info chave valor
Exemplo: "new info email joao@example.com"

del info
Descrição: Exclui uma chave e seu valor associado da configuração
Uso: del info chave
Exemplo: "del info email"

set color
Descrição: Define a cor do texto para o console ou prompt de entrada
Uso: set color [console/input] [cor]
Exemplo: "set color console azul"

open
Descrição: Abre um arquivo com o aplicativo padrão
Uso: open caminho_do_arquivo
Exemplo: "open C:/Documentos/exemplo.txt"

run/start
Descrição: Executa a função 'start' no bot

finish/stop
Descrição: Fecha a janela da aplicação

change theme
Descrição: Alterna entre os temas escuro e claro
Uso: change theme

clear
usado para limpar todos os textos e logs no terminal
"""

# Verificar e criar os arquivos help.txt e help2.txt se necessário
verificar_arquivo_help('help.txt', conteudo_help)
verificar_arquivo_help('help2.txt', conteudo_help2)
# Verificar e criar o arquivo settings.txt se necessário
verificar_arquivo_settings()
