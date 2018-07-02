import json
import requests
import time
import urllib
import os
import pandas as pd
import random
from geopy.distance import great_circle
from telegram import keyboardbutton, ReplyKeyboardMarkup

TOKEN = "497980376:AAGVpWuIksVtHUVJVvn0Gi4mcPbdyR873z0"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
DDURL = "https://medialab-prado.github.io/doctordata/telegram-map.html"

location_test = {'latitude':40.4523, 'longitude': -3.7896}

pwd = os.getcwd()[:-4]
#pwd = '/Volumes/MacintoshHD/_GitHub/doctordata/bot'
cwd = pwd + '/api/csv/'
jwd = pwd + '/api/json/'
bwd = pwd + '/bot/'
dwd = pwd + '/api/data/'

#bwd = '/Volumes/MacintoshHD/_GitHub/doctordata/bot/'
os.chdir(dwd)
os.listdir()
indice = pd.read_csv('indice.csv',delimiter=';',index_col=0)
indice.columns
os.chdir(cwd)
os.listdir()
filelist = [ f for f in os.listdir(cwd) if f.endswith("-missing_AYU.csv") ]
datalist = []

for fichero in filelist:
    data = pd.read_csv(fichero)
    data['bot'] = indice[indice['palabra']==fichero.split('-')[1]]['bot'].values[0]
    datalist.append(data)
data = pd.concat(datalist)
data.columns = ['id_OSM','latitude','longitude','coordinates','bot']

testList = data.to_dict(orient='records')
location = {}
os.chdir(bwd)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
            send_location([40.35,-3.78],chat)
        except Exception as e:
            print(e)

def send_location(location, chat_id, date):
    url = URL + "sendlocation?chat_id={}&latitude={}&longitude={}".format(chat_id, location['latitude'],location['longitude'])
    get_url(url)
    with open('retos.json','a') as myfile:
        reto = {'date':date, 'chat':chat_id, 'location':location}
        stringJson = json.dumps(reto)
        myfile.write(stringJson+'\n')
        myfile.close()

def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def set_score(chat_id, text, date):
    with open('scores.json','a') as myfile:
        score = {'date':date, 'chat':chat_id, 'text':text}
        stringJson = json.dumps(score)
        myfile.write(stringJson+'\n')
        myfile.close()

def handle_updates(updates):
    for update in updates["result"]:
        with open('updates.json','a') as myfile:
            stringJson = json.dumps(update)
            myfile.write(stringJson+'\n')
        myfile.close()
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            date = update["message"]["date"]
            first_name = update["message"]["from"]["first_name"]

            if text == "/start":
                keyboard = build_keyboard(['Comenzamos!','Reto del día','Más info','Salir'])
                send_message("Hola {}, soy DoctorData, tu bot colaborativo para mejorar entre todos los datos abiertos de la web del ayuntamiento de Madrid.".format(first_name), chat, keyboard)

            if text == "/doctordata":
                send_message(DDURL+'?dataset=fuentes&latitude=40.35&longitude=-3.78&zoom=18'.format(chat),chat)

            if text == 'Hola' or text == 'hola':
                keyboard = build_keyboard(['Comenzamos!','Reto del día','Más info','Salir'])
                send_message('Hola, dime qué te apetece hoy.',chat, keyboard)
                send_message('Si haces click en Comenzamos! te enviaré retos aleatorios, si me envías tu ubicación mucho mejor, porque estarán cerca tuya..',chat, keyboard)
                send_message('Si por el contrario te apetece un buen reto, prueba el reto del día donde competirás con otros madrileños por ser el primero en responder.',chat, keyboard)


            if text != '':
                keyboard = build_keyboard(['Comenzamos!','Reto del día','Más info','Salir'])

            if text == 'Reto del día':
                keyboard = build_keyboard(['Sí, existe','No, no existe','Otro al azar','Otro cercano','Salir'])
                send_message('Dime si existe esta fuente!',chat, keyboard)
                send_location(location_test, chat, date)

            if text == 'Más info':
                keyboard = build_keyboard(['Comenzamos!','Salir'])
                send_message("Este bot forma parte de un proyecto presentado al concurso de Medialab Prado #Datamad2017.\nCon él pretendemos mejorar los datos disponibles en el portal de datos del Ayuntamiento y que todos colaboremos en mantenerlos al día.", chat, keyboard)
                send_message("Al responder a cada reto nos aportas información sobre elementos de tu ciudad, su estado de conservación, o simplemente si existen.", chat, keyboard)
                send_message("Con tu colaboración hacemos mejor la información pública de nuestra ciudad y ayudamos/exigimos a la administración a mejorar.", chat, keyboard)
                send_message("Ni que decir tiene que toda la información recopilada se trata de forma totalmente anónima y en cualquier momento puedes dirigirte a nosotros para borrarla o si quieres más info.", chat, keyboard)
                send_message("Rai y Esteban. Equipo de DoctorData", chat, keyboard)
                send_message("https://medialab-prado.github.io/doctordata/",chat, keyboard)

            if text == 'Exit' or text == 'Salir':
                keyboard = build_keyboard(['Comenzamos de nuevo!','Más info','Salir'])
                send_message("Gracias por usar este servicio. Recuerda que estaré por aquí para cuando quieras jugar!", chat, keyboard)

            if text == 'Comenzamos!' or text == 'Comenzamos de nuevo!':
                #location_keyboard = keyboardbutton(text='Send location', request_location = True)
                #reply_keyboard = [[location_keyboard]]
                #custom_keyboard = [[location_keyboard]]

                keyboard = build_keyboard(['Reto del día','Uno cercano a mi última ubicación','Uno al azar','Salir'])
                #keyboard = build_keyboard_location(['Enviar ubicación'])
                send_message("Necesito que me envíes tu ubicación. Así podré buscarte retos cercanos. Si no quieres compartir tu ubicación puedes elegir Uno al azar con los botones de abajo.", chat, keyboard)

            if text == 'Sí, existe':
                keyboard = build_keyboard(['Sí, funciona!','No, no funciona','Otro cercano','Salir'])
                send_message("Genial! Muchas gracias por ayudar! Funciona???", chat, keyboard)
                set_score(chat,text,date)

            if text == 'Sí, funciona!':
                keyboard = build_keyboard(['Comenzamos de nuevo!','Reto del día','Otro cercano','Salir'])
                send_message("Genial, muchas gracias por ayudar!", chat, keyboard)
                set_score(chat,text,date)

            if text == 'No, no funciona':
                keyboard = build_keyboard(['Comenzamos de nuevo!','Otro cercano','Salir'])
                send_message("Vale, avisaremos a mantenimiento.", chat, keyboard)
                set_score(chat,text,date)

            if text == 'No, no existe':
                keyboard = build_keyboard(['Comenzamos de nuevo!','Salir'])
                send_message("Vale, estos son los errores que queremos corregir y gracias a tu ayuda lo haremos!", chat, keyboard)
                set_score(chat,text,date)

            if text == 'No sé!':
                keyboard = build_keyboard(['Comenzamos de nuevo!','Salir'])
                send_message("Vaya... he metido la pata seguro...", chat, keyboard)
                set_score(chat,text,date)

            if text == 'Otro' or text =='Otro cercano' or text == 'Uno cercano a mi última ubicación':
                try:
                    datos = pd.read_csv(str(chat)+'.csv')
                    datos.count()['id_OSM']
                    random.randint(0,25)
                    test = datos.loc[random.randint(0, datos.count()['id_OSM']-1)]
                    location = {'latitude':test['latitude'],'longitude':test['longitude'],'type':test['bot']}
                    keyboard = build_keyboard(['Sí, existe','No, no existe','Otro cercano','Salir'])
                    send_message('Ahí va! Del dataset {}s. ¿Está ahí?'.format(location['type']),chat, keyboard)
                    send_location(location, chat, date)
                except:
                    keyboard = build_keyboard(['Comenzamos de nuevo!','Más info','Salir'])
                    send_message("No tengo ninguna ubicación tuya aún..",chat, keyboard)


            if text == 'Uno al azar':
                keyboard = build_keyboard(['Sí, existe','No, no existe','Otro al azar','Otro cercano','Salir'])
                send_message('Interesante, te gustan los retos... Dime si existe esta fuente!',chat, keyboard)
                location_random = random.choice(testList)
                send_location(location_random, chat, date)

            if text == 'Otro al azar':
                keyboard = build_keyboard(['Sí, existe','No, no existe','Otro al azar','Otro cercano','Salir'])
                location_random = random.choice(testList)
                send_message('Dime si existe esta fuente!',chat, keyboard)
                send_location(location_random, chat, date)


        except Exception as e:
            print(e)
            try:
                location = update["message"]["location"]
                date = update["message"]["date"]
                chat = update["message"]["chat"]["id"]
                keyboard = build_keyboard(['Sí, existe','No, no existe','Otro','Salir'])
                send_message('Genial, un segundo que voy a buscarte un reto cercano.',chat, keyboard)
                location = get_close_test(location, data, chat)
                send_message('¿Hay aquí un@ {}?'.format(location['type']),chat, keyboard)
                send_location(location, chat, date)

            except Exception as e:
                print(e)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def build_keyboard_location(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True, "request_location":True}
    return json.dumps(reply_markup)

def get_close_test(location,data, chat_id,random_opt = False):
    datas = data.copy()
    datas['close'] = datas['coordinates'].apply(lambda x: getDistance_meters(x, (location['latitude'],location['longitude'])))
    datas = datas.sort_values('close')
    if random_opt:
        location['latitude'] = data.loc[random.choice(range(10))]['latitude']
        location['longitude'] = data.loc[random.choice(range(10))]['longitude']

    location['latitude'] = datas.head(1)['latitude'].values[0]
    location['longitude'] = datas.head(1)['longitude'].values[0]
    location['type'] = datas.head(1)['bot'].values[0]
    datas.set_index('id_OSM',inplace=True)
    datas.head(15).to_csv(str(chat_id)+'.csv')
    return location

def getDistance_meters(x,y):
    try:
        return great_circle(x, y).kilometers*1000.0
    except:
        return 0

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
