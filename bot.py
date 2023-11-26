import json
from tkinter import *
from extract import class_prediction, get_response
from keras.models import load_model
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import train

historicoPerguntas = []
melhorarRespostas = []

# extraimos o modelo usando o keras
model = load_model('model.h5')

# carregamos nossas intenções
intents = json.loads(open('intents.json', encoding='utf-8').read())

base = Tk()
base.title("Chatbot")
base.geometry("750x460")
base.resizable(width=FALSE, height=FALSE)

def horadatanow():
    now = datetime.now()
    return ("Agora são " + now.strftime("%H:%M do dia %d/%m/%Y "))

def pesquisa(msg, res):
    try:
        page = requests.get("https://www.google.com/search?q=" + str(msg)).text
        soup = BeautifulSoup(page, "html.parser").select(".s3v9rd.AP7Wnd")
        pesq = int(res[9:])
        print(pesq)
        res = soup[pesq].getText(strip=True)
        print(res)
        for x in range(len(res)):
            if res[x - 1:x] == "." and x > 200:
                res = res[:x]
                break
    except:
        res = "Algo deu errado, verifique se estou conectado a internet :("
    return res


def chatbot_response(msg):
    ints = class_prediction(msg, model)
    res = get_response(ints, intents)
    pergunta = False
    melhorar = False
    ordemDeBusca = 0
    print(res)
    if res[:8] == "PESQUISA":
        ordemDeBusca = int(res[9:])
        res = pesquisa(msg,res)
        pergunta = True
    elif res == "TIMEDAY":
        res = horadatanow()
    print(res)
    if res[:8] == "Desculpa":
        melhorar = True
    return res, pergunta, ordemDeBusca, melhorar

def send():
    global melhorarRespostas, historicoPerguntas
    """
        Envia a mensagem
    """
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)
    if msg != '':
        Chat.config(state=NORMAL)
        Chat.insert(END, f"Você: {msg}\n\n", 'tag-left')
        Chat.config(foreground="#000000", font=("Arial", 12))
        response, pergunta, ordem, melhorar = chatbot_response(msg)
        historicoPerguntas.append([msg, ordem])
        print(historicoPerguntas)
        Chat.insert(END, f"Bot: {response}\n\n", 'tag-left')
        if pergunta:
            Newresponse = "Essa informação foi útil?"
            Chat.insert(END, f"Bot: {Newresponse}\n\n", 'tag-left')
        if melhorar:
            melhorarRespostas.append(historicoPerguntas[len(historicoPerguntas) - 2].copy())
            if historicoPerguntas[len(historicoPerguntas)-2][1] == 5:
                Newresponse = "Cheguei no meu limite para essa pergunta, não consigo melhorar a resposta dela :("
                Chat.insert(END, f"Bot: {Newresponse}\n\n", 'tag-left')
        Chat.config(state=DISABLED)
        Chat.yview(END)

def on_closing():
    global melhorarRespostas
    charge = False
    print("fechou")
    print(melhorarRespostas)
    with open('intents.json', 'r',encoding='utf-8') as file:
        file_data = json.load(file)
        print(file_data)
    with open('intents.json', 'w', encoding='utf-8') as file:
        for add in melhorarRespostas:
            if add[1] != 0 and add[1] != 5:
                print("a pergunta: ", add, ", foi incorporada")
                charge = True
                file_data['intents'][add[1]]['patterns'].append(add[0])
                if add[1] != 1:
                    try:
                        file_data['intents'][add[1]-1]['patterns'].remove(add[0])
                    except:
                        pass
            elif add[1] == 5:
                try:
                    file_data['intents'][add[1]-1]['patterns'].remove(add[0])
                except:
                    pass
                charge = True
        file.seek(0)
        json.dump(file_data, file, indent=4, ensure_ascii=False)
    if charge:
        train.main()
    base.destroy()


# Cria a janela do chat
Chat = Text(base, bd=0, bg="white", height="8", width="50", font="Arial", wrap=WORD)
Chat.tag_configure('tag-left', justify=LEFT)
Chat.config(state=DISABLED)

# Vincula a barra de rolagem à janela de bate-papo
scrollbar = Scrollbar(base, command=Chat.yview)
Chat['yscrollcommand'] = scrollbar.set

# Cria o botão de envio de mensagem, onde o comando envia para a função de send
SendButton = Button(base, font=("Verdana", 10, 'bold'), text="Enviar", width="12", height=2, bd=0, bg="#666", activebackground="#333", fg='#ffffff', command=send)

# Cria o box de texto
EntryBox = Text(base, bd=0, bg="white", width="29", height="2", font="Arial")

# Coloca todos os componentes na tela
scrollbar.place(x=726, y=6, height=386)
Chat.place(x=6, y=6, height=386, width=720)
EntryBox.place(x=128, y=401, height=50, width=600)
SendButton.place(x=6, y=401, height=50)

base.protocol("WM_DELETE_WINDOW", on_closing)
base.mainloop()