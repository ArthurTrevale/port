from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import webbrowser
import threading
from datetime import datetime
import time
import keyboard
from random import randint
import customtkinter
from customtkinter import *
from customtkinter import ALL
import threading
import pyautogui
from selenium.webdriver.common.action_chains import ActionChains
import re
from openai import OpenAI
from dotenv import load_dotenv
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tsu
from PIL.Image import open as pillow_image_open
from PIL import ImageTk,Image,ImageFilter



load_dotenv()
tsu.verificar_arquivo_settings()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

#Váriaveis de ambiente ou inicializadoras
#################################################################################################################################################################

botao_ligado = False
parar_robo = threading.Event()
thread_robo = None
base_link=tsu.get("Url")
resposta_site=""
textos_botão=['Stop','Running','Not Defined','New Url','Set Value','New Key']
count=int(tsu.get('Time'))
cor_bordas=["#57cc5b","#57cc5b"]
cor_textos=["black","black"]
version = "V 0.0.5 Alpha Test"
comandos_cache = []
sugestoes_autocompletar = ["set","get","new","del","info","open","run","finish","stop", "color", "console", "input", "help","clear","change theme"]

#Funções internas
#################################################################################################################################################################

def is_valid_link(link):
    # Padrão regex para verificar se é uma URL válida
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # Domínio...
        r'localhost|'  # ou localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ou endereço IP
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ou endereço IP com notação IPv6
        r'(?::\d+)?'  # e porta opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    return re.match(url_pattern, link) is not None

def api_vison(a,b):
    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        prompt_type = int(a)
    except ValueError:
        prompt_type = 6
    url = b
    
    if prompt_type == 1:
        completion = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": "sou deficiente visual, e a imagem  em questão não possui acessibilidade, oque está escrito ?"},
                {
                "type": "image_url",
                "image_url": {
                    "url": f"{b}",
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
        
    else:
        return "erro na api, escolha um valor inteiro entre [0-1]",206
    
    return completion.choices[0].message.content

def adicionar_log(mensagem):
    log.configure(state=customtkinter.NORMAL)
    log.insert(customtkinter.END, mensagem + "\n")
    log.configure(state=customtkinter.DISABLED)
    log.see(customtkinter.END)

def inicializar_robo():
    if tsu.get('url') != "":
        try:
            def robo_thread():
                global count
                adicionar_log("Thread inicializada")
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--window-size=640,480")
                chrome_options.add_argument("--incognito")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument('--disable-infobars')
                servico = Service(ChromeDriverManager().install())
                navegador = webdriver.Chrome(service=servico, options=chrome_options)
                navegador.get(tsu.get("Url"))
                navegador.find_element('xpath',tsu.get('Clogin')).send_keys(tsu.get('User'))
                navegador.find_element('xpath',tsu.get('Cpassword')).send_keys(tsu.get('Password'))
                if tsu.get('captcha') != '':
                    adicionar_log("esse site possui um captcha")
            
                count = int(tsu.get('Time'))
                time.sleep(count)
                
                adicionar_log("Running the 2 step...")
                try:
                    navegador.get(tsu.get('Url2'))
                    time.sleep(3)
                except Exception as e:
                    adicionar_log(f"Ocorreu um erro fora da função: {e}")
                # Loop até que o evento seja definido para encerrar a thread
                while not parar_robo.is_set():
                    time.sleep(1)

                navegador.quit()  # Fecha o navegador quando a thread é encerrada
                adicionar_log("Thread encerrada")

            global thread_robo
            thread_robo = threading.Thread(target=robo_thread)
            thread_robo.start()

        except Exception as e:
            adicionar_log(f"Ocorreu um erro fora da função: {e}")

    else:
        top = customtkinter.CTkToplevel(jan)
        top.geometry("480x320")
        top.title("Get Initial Infos")
        top.resizable(width=False,height=False)
        top.grab_set()
        

        entry1 = customtkinter.CTkEntry(top, placeholder_text="User", placeholder_text_color="Blue")
        entry1.grid(row=0, column=0, padx=10, pady=10)

        entry2 = customtkinter.CTkEntry(top, placeholder_text="Password", placeholder_text_color="Blue")
        entry2.grid(row=1, column=0, padx=10, pady=10)

        entry3 = customtkinter.CTkEntry(top, placeholder_text="Link/Url", placeholder_text_color="Blue")
        entry3.grid(row=2, column=0, padx=10, pady=10)

        entry4 = customtkinter.CTkEntry(top, placeholder_text="Secounds Time", placeholder_text_color="Blue")
        entry4.grid(row=3, column=0, padx=10, pady=10)

        entry5 = customtkinter.CTkEntry(top, placeholder_text="Login Input -> Xpath", placeholder_text_color="Blue")
        entry5.grid(row=0, column=1, padx=10, pady=10)

        entry6 = customtkinter.CTkEntry(top, placeholder_text="Password Input -> Xpath", placeholder_text_color="Blue")
        entry6.grid(row=1, column=1, padx=10, pady=10)

        entry7 = customtkinter.CTkEntry(top, placeholder_text="Captcha -> Xpath if exists", placeholder_text_color="Blue")
        entry7.grid(row=2, column=1, padx=10, pady=10)

        def internal_function_to_set_tsu_base():
            # Obter os valores dos campos de entrada
            user_value = entry1.get()
            password_value = entry2.get()
            link_value = entry3.get()
            time_value = entry4.get()
            login_xpath_value = entry5.get()
            password_xpath_value = entry6.get()
            captcha_xpath_value = entry7.get()

            # Verificar se algum campo está vazio
            if not all([user_value, password_value, link_value, time_value, login_xpath_value, password_xpath_value, captcha_xpath_value]):
                adicionar_log("there are fields not filled in, this may cause errors")
                return
            
            # Executar a função tsu.set() com os valores obtidos
            tsu.set('User', user_value)
            tsu.set('Password', password_value)
            tsu.set('Url', link_value)
            tsu.set('Time', time_value)
            tsu.set('Clogin', login_xpath_value)
            tsu.set('Cpassword', password_xpath_value)
            tsu.set('Captcha', captcha_xpath_value)
        button = customtkinter.CTkButton(top, text="Set", command=internal_function_to_set_tsu_base)
        button.grid(row=3, column=1, padx=10, pady=10)
        top.wait_window()

def get_date():
    data_atual = datetime.now()

# Converter para uma string no formato desejado
    data_em_string = data_atual.strftime("%d/%m/%Y")
    return data_em_string

def comand(event):
    comando = prompt.get()
    comandos_cache.append(comando)
    global indice_cache
    indice_cache = len(comandos_cache)
    prompt.delete(0, 'end')

    if comando == 'get infos':
        ta = str(tsu.get_all())
        adicionar_log(ta)

    elif comando == 'set infos':
        top = customtkinter.CTkToplevel(jan)
        top.geometry("480x320")
        top.title("Get Initial Infos")
        top.resizable(width=False,height=False)
        top.grab_set()
        

        entry1 = customtkinter.CTkEntry(top, placeholder_text="User", placeholder_text_color="Blue")
        entry1.grid(row=0, column=0, padx=10, pady=10)

        entry2 = customtkinter.CTkEntry(top, placeholder_text="Password", placeholder_text_color="Blue")
        entry2.grid(row=1, column=0, padx=10, pady=10)

        entry3 = customtkinter.CTkEntry(top, placeholder_text="Link/Url", placeholder_text_color="Blue")
        entry3.grid(row=2, column=0, padx=10, pady=10)

        entry4 = customtkinter.CTkEntry(top, placeholder_text="Secounds Time", placeholder_text_color="Blue")
        entry4.grid(row=3, column=0, padx=10, pady=10)

        entry5 = customtkinter.CTkEntry(top, placeholder_text="Login Input -> Xpath", placeholder_text_color="Blue")
        entry5.grid(row=0, column=1, padx=10, pady=10)

        entry6 = customtkinter.CTkEntry(top, placeholder_text="Password Input -> Xpath", placeholder_text_color="Blue")
        entry6.grid(row=1, column=1, padx=10, pady=10)

        entry7 = customtkinter.CTkEntry(top, placeholder_text="Captcha -> Xpath if exists", placeholder_text_color="Blue")
        entry7.grid(row=2, column=1, padx=10, pady=10)

        def internal_function_to_set_tsu_base():
            # Obter os valores dos campos de entrada
            user_value = entry1.get()
            password_value = entry2.get()
            link_value = entry3.get()
            time_value = entry4.get()
            login_xpath_value = entry5.get()
            password_xpath_value = entry6.get()
            captcha_xpath_value = entry7.get()

            # Verificar se algum campo está vazio
            if not all([user_value, password_value, link_value, time_value, login_xpath_value, password_xpath_value, captcha_xpath_value]):
                adicionar_log("there are fields not filled in, this may cause errors")
                return
            
            # Executar a função tsu.set() com os valores obtidos
            tsu.set('User', user_value)
            tsu.set('Password', password_value)
            tsu.set('Url', link_value)
            tsu.set('Time', time_value)
            tsu.set('Clogin', login_xpath_value)
            tsu.set('Cpassword', password_xpath_value)
            tsu.set('Captcha', captcha_xpath_value)
        button = customtkinter.CTkButton(top, text="Set", command=internal_function_to_set_tsu_base)
        button.grid(row=3, column=1, padx=10, pady=10)
        top.wait_window()

    elif 'set info' in comando:
        try:
            partes = comando.split()
            key=partes[-2]
            value=partes[-1]
            res=tsu.set(key,value)
            adicionar_log(f"{res}")
        except Exception or ValueError or TypeError as e:
            adicionar_log(f'erro: {e}')

    elif 'get info' in comando:
        try:
            partes = comando.split()
            key=partes[-1]
            response=tsu.get(key)
            adicionar_log(f"Value in {key}: {response}")
        except Exception or ValueError or TypeError as e:
            adicionar_log(f'erro: {e}')

    elif 'new info' in comando:
        try:
            partes = comando.split()
            key=partes[-2]
            value=partes[-1]
            res=tsu.new(key,value)
            adicionar_log(f"Created Key: {key} and set the initial value as {value}")
        except Exception or ValueError or TypeError as e:
            adicionar_log(f'erro: {e}')

    elif 'del info' in comando:
        try:
            partes = comando.split()
            key=partes[-1]
            res=tsu.delete_key(key)
            adicionar_log(f"{res}")
        except Exception or ValueError or TypeError as e:
            adicionar_log(f'erro: {e}')

    elif 'set color' in comando:
        if 'console' in comando:
            try:
                numero_cor = comando.split()[-1]
                numero_cor2 = comando.split()[-2]
                try:
                    if numero_cor2:
                        cor_escolhida = numero_cor
                        log.configure(text_color=cor_escolhida)
                        adicionar_log(">>>")
                except:
                    adicionar_log(">>>")
                    
                if numero_cor:
                    cor_escolhida = numero_cor2
                    log.configure(fg_color=cor_escolhida)
            except ValueError:
                adicionar_log("error")
        elif 'input' in comando:
            try:
                numero_cor = comando.split()[-1]
                numero_cor2 = comando.split()[-2]
                try:
                    if numero_cor2:
                        cor_escolhida = numero_cor
                        prompt.configure(text_color=cor_escolhida)
                        adicionar_log(">>>")
                except:
                    adicionar_log(">>>")
                    
                if numero_cor:
                    cor_escolhida = numero_cor2
                    prompt.configure(fg_color=cor_escolhida)
            except ValueError:
                adicionar_log("error")
        else:
            adicionar_log("missing argument 'console' or 'input'")
    
    elif 'open' in comando:
        partes = comando.split()
    
        if len(partes) == 2 and partes[0] == 'open':
            caminho = partes[1]
            
            if os.path.exists(caminho):
                try:
                    os.startfile(caminho)
                    adicionar_log(f"file '{caminho}' sucess")
                except Exception as e:
                    adicionar_log(f"Error to open '{caminho}': {e}")
            else:
                adicionar_log(f">>> '{caminho}' not found")
        else:
            adicionar_log("comand 'open' bad format")
    
    elif comando == 'run' or comando == 'start':
        on_off()

    elif comando == 'finish' or comando =='stop':
        jan.destroy()

    elif comando == 'change theme':
        valor = tsu.get('theme')

        if valor == "False":
            customtkinter.set_appearance_mode("dark")
            prompt.configure(text_color='yellow')

            frame1.configure(border_color=cor_bordas[0])
            frame2.configure(border_color=cor_bordas[0])
            frame3.configure(border_color=cor_bordas[0])
            mini_frame1.configure(border_color=cor_bordas[0])

            label1.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])
            label2.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])
            label3.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])
            mini_label1.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])

            log.configure(text_color="#00BFFF")
            tsu.set('theme','True')
            adicionar_log('exchanged')
        else:
            customtkinter.set_appearance_mode("light")
            prompt.configure(text_color='black')

            frame1.configure(border_color=cor_bordas[1])
            frame2.configure(border_color=cor_bordas[1])
            frame3.configure(border_color=cor_bordas[1])
            mini_frame1.configure(border_color=cor_bordas[1])

            label1.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])
            label2.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])
            label3.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])
            mini_label1.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])

            log.configure(text_color="#483D8B")
            tsu.set('theme','False')
            adicionar_log('exchanged')

    elif comando == 'help' or comando == 'help pt':
        if 'pt' in comando:
            res=tsu.get_help(1)
            adicionar_log(res)
        else:
            res=tsu.get_help(0)
            adicionar_log(res)

    elif comando == 'clear':
        limpar_terminal()

    elif comando == 'system info':
        comand('get infos')
        adicionar_log(version)
        adicionar_log('threads: 0 -> 1')
        data = get_date()
        adicionar_log(f'Last verification: {data}')

    elif comando == 'suport':
        falar_com_dev()

    else:
        adicionar_log(f"the command [{comando}] was not recognized")

def thema():
        valor = tsu.get('theme')
        if valor == "True":
            customtkinter.set_appearance_mode("dark")
            prompt.configure(text_color='yellow')

            frame1.configure(border_color=cor_bordas[0])
            frame2.configure(border_color=cor_bordas[0])
            frame3.configure(border_color=cor_bordas[0])
            mini_frame1.configure(border_color=cor_bordas[0])

            label1.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])
            label2.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])
            label3.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])
            mini_label1.configure(bg_color=cor_bordas[0],text_color=cor_textos[0])

            log.configure(text_color="#00BFFF")

        else:
            customtkinter.set_appearance_mode("light")
            prompt.configure(text_color='black')

            frame1.configure(border_color=cor_bordas[1])
            frame2.configure(border_color=cor_bordas[1])
            frame3.configure(border_color=cor_bordas[1])
            mini_frame1.configure(border_color=cor_bordas[1])

            label1.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])
            label2.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])
            label3.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])
            mini_label1.configure(bg_color=cor_bordas[1],text_color=cor_textos[1])

            log.configure(text_color="#483D8B")

def limpar_terminal():
    log.configure(state=customtkinter.NORMAL)
    log.delete("1.0", customtkinter.END)
    log.configure(state=customtkinter.DISABLED)

def falar_com_dev():
    webbrowser.open("https://api.whatsapp.com/send/?phone=5584981742153&text=I need help using the bot, please can you help me?")

def comando_anterior(event):
    global indice_cache
    if indice_cache > 0:
        indice_cache -= 1
        prompt.delete(0, 'end')
        prompt.insert(0, comandos_cache[indice_cache])

def comando_posterior(event):
    global indice_cache
    if indice_cache < len(comandos_cache) - 1:
        indice_cache += 1
        prompt.delete(0, 'end')
        prompt.insert(0, comandos_cache[indice_cache])

def auto_completar(event):
    entrada = prompt.get()
    palavras = entrada.split()

    if len(palavras) > 0:
        palavra_atual = palavras[-1]
        sugestoes = [sugestao for sugestao in sugestoes_autocompletar if sugestao.startswith(palavra_atual)]

        if sugestoes:
            sugestao = sugestoes[0]
            entrada_completa = entrada.rstrip(palavra_atual) + sugestao
            prompt.delete(0, "end")
            prompt.insert(0, entrada_completa)
            prompt.icursor("end")

#################################################################################################################################################################

# Funções chamadas pelos botões
#################################################################################################################################################################

def on_off():
    global botao_ligado, thread_robo
    try:
        if botao_ligado:
            adicionar_log("Finalizando...")
            parar_robo.set()  # Define o evento para finalizar a thread
            botao.configure(text=textos_botão[0], fg_color="red")
        else:
            if not thread_robo or not thread_robo.is_alive():
                parar_robo.clear()
                inicializar_robo()
                adicionar_log("Inicializado, com sucesso!")
            botao.configure(text=textos_botão[1], fg_color="green")
    except Exception as e:
        adicionar_log(f"Ocorreu um erro: {e}")
    finally:
        botao_ligado = not botao_ligado

def inputar_link():
    global base_link
    try:
        adicionar_log("Url validation...")
        inputed_link = customtkinter.CTkInputDialog(text="Novo Link", title="Novo Link")
        base_link=tsu.set('Url',inputed_link.get_input())
    except Exception as e:
        base_link = "https://www.bmgconsig.com.br/Index.do?method=prepare"
        adicionar_log(">>>")

def inputar_param():
    global count
    inputed_value = customtkinter.CTkInputDialog(text="Informe a chave e o valor separados por vírgula (ex: chave,valor):", title="Chave e Valor")

    try:
        new_value = inputed_value.get_input()
        key, value = map(str.strip, new_value.split(','))
        tsu.set(key, value)
    except Exception as e:
        adicionar_log(f"Erro ao processar entrada: {e}")

def inputar_key():
    inputed_value = customtkinter.CTkInputDialog(text="Novo Valor Chave", title="Novo Valor Chave")
    tsu.new(inputed_value.get_input(),'')

#################################################################################################################################################################

#Janela
#################################################################################################################################################################
  
jan = customtkinter.CTk()
path = "zis\\logo-icon-green.ico"
jan.iconbitmap(path)
jan.geometry("720x640")
jan.title(f"Kemo-Tuts {version}")
jan.resizable(width=False,height=False)

#################################################################################################################################################################

#Progress bar
#################################################################################################################################################################
my_image = customtkinter.CTkImage(Image.open("zis\\logo.png"),size=(150, 73))
logo_lugar = CTkLabel(jan, image=my_image, text="")
logo_lugar.place(relx=0.1, rely=0.01, relwidth=0.8, relheight=0.10)

#################################################################################################################################################################

#Frames
#################################################################################################################################################################

frame1 = customtkinter.CTkFrame(jan,fg_color="transparent",border_color=cor_bordas[0],border_width=4)
frame1.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.2)

frame2 = customtkinter.CTkFrame(jan,fg_color="transparent",border_color=cor_bordas[0],border_width=4)
frame2.place(relx=0.1, rely=0.35, relwidth=0.8, relheight=0.2)

frame3 = customtkinter.CTkFrame(jan,fg_color="transparent",border_color=cor_bordas[0],border_width=4)
frame3.place(relx=0.1, rely=0.6, relwidth=0.8, relheight=0.39)

mini_frame1 = customtkinter.CTkFrame(frame3,fg_color="transparent",border_color=cor_bordas[0],border_width=4)
mini_frame1.place(relx=0.01, rely=0.12, relwidth=0.8, relheight=0.12)

#################################################################################################################################################################

#Labels
#################################################################################################################################################################

label1= customtkinter.CTkLabel(frame1,text="Configs",bg_color=cor_bordas[0],corner_radius=100)
label1.place(relx=0.0,rely=0.0)

label2= customtkinter.CTkLabel(frame2,text="Start/Off",bg_color=cor_bordas[0],corner_radius=100)
label2.place(relx=0.0,rely=0.0)

label3= customtkinter.CTkLabel(frame3,text="Console Log Section",bg_color=cor_bordas[0],corner_radius=100)
label3.place(relx=0.0,rely=0.0)

mini_label1= customtkinter.CTkLabel(mini_frame1,text="Prompt",bg_color=cor_bordas[0],corner_radius=100)
mini_label1.place(relx=0.0,rely=0.0)

#################################################################################################################################################################

#Botões
#################################################################################################################################################################

botao = customtkinter.CTkButton(frame2, text=textos_botão[0], fg_color="red", command=on_off)
botao.place(relx=0.05, rely=0.233)

botao_link = customtkinter.CTkButton(frame1, text=textos_botão[3], command=inputar_link)
botao_link.place(relx=0.05,rely=0.233)

botao_link = customtkinter.CTkButton(frame1, text=textos_botão[4], command=inputar_param)
botao_link.place(relx=0.30,rely=0.233)

botao_link = customtkinter.CTkButton(frame1, text=textos_botão[5], command=inputar_key)
botao_link.place(relx=0.55,rely=0.233)

#################################################################################################################################################################

#Text_boxs
#################################################################################################################################################################

log = customtkinter.CTkTextbox(frame3, state=customtkinter.DISABLED, wrap="word", text_color="#00BFFF")
log.place(relx=0.02, rely=0.32, relwidth=0.97, relheight=0.64)

#################################################################################################################################################################

#Entry
#################################################################################################################################################################

prompt = customtkinter.CTkEntry(mini_frame1,placeholder_text=">>>>>>>>>>>",text_color="Yellow")
prompt.place(relx=0.15, rely=0.08, relwidth=0.84, relheight=0.76)
prompt.bind("<Return>", comand)
prompt.bind("<Up>", comando_anterior)
prompt.bind("<Down>",comando_posterior)
prompt.bind("<Right>", auto_completar)

#################################################################################################################################################################

#loop
#################################################################################################################################################################

thema()
jan.mainloop()

#################################################################################################################################################################

#trheads list
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-inicializar robô  + 1 thread
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#cores:
#  #008B8B  - bordas
#  #00BFFF  - saida do console

#campos

#new link propose âncora
#new link nova proposta

#https://api.whatsapp.com/send/?phone=