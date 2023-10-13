import os 
import telebot

import requests
import json
import random

# send graph to telebot 
import numpy as np
import pandas as pd

from datetime import datetime
import redis

import pickle

import yfinance as yf
#import plotly

from dotenv import load_dotenv
load_dotenv()
#import plotly.graph_objs as go
from telebot import types

import translators as ts

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

motivation = ["Portföyünüzü lezzetlendirin, çeşitlendirin.",
 "Finans hedeflerinizi tarif gibi hazırlayın.",
 "Risk yönetimi, mutfakta tuz kullanmak gibidir.",
 "Finansal kararlar iz bırakır, malzemeler önemlidir.",
 "Zamanlama her şeydir, yatırımlarda da.",
 "Çeşitlilik dengede lezzet yaratır.",
 "Başarı, sabır ve beceri gerektirir.",
 "Risk yönetimi, dengeyi korumaktır.",
 "Portföyünüzü seçerken, yatırımınıza baharat katın.",
 "Finansal başarı, en iyi malzemelerle başlar.",
 "Risk yönetimi, mutfakta denge sağlamak gibidir.",
 "Her yatırım kararı, yemek tarifleri gibi özenle hazırlanmalıdır.",
 "Zamanlamayı iyi ayarlamak, yatırımlarda ve yemek pişirmede önemlidir.",
 "Çeşitlendirme, lezzetli bir yemeği andırır: Her şey dengede olmalı.",
 "Finansal başarı, ustalıkla pişirilmiş bir yemeği andırır: Sabır ve özen gerektirir.",
 "Riskleri dengeleyin, finansal lezzetin tadını çıkarın.",
 "Yatırım portföyünüzü pişirin, dengede tutun.",
 "Finans hedeflerinizi tatlı bir başarıya dönüştürün.",
 "Risk yönetimi, mutfakta tat ve dengenin anahtarıdır.",
 "Her finansal hamle, yemek tarifleri gibi özen ve öğrenme gerektirir.",
 "Zamanlama, yatırımlarınızın pişme süresidir; sabır önemlidir.",
 "Portföy çeşitlendirmesi, yemeklerin çeşitliliği gibidir; dengeli olmalı.",
 "Finansal başarı, mükemmel malzemelerle başlar: Planlayın ve uygulayın.",
 "Riskleri yönetin, finans dünyasının lezzetini çıkarın.",
 "Finans hedeflerinizin tadını çıkarın, başarıyı yavaş pişirin.",
 "Her finansal adım, mükemmel bir yemek gibi özen ister: Planlamayı unutmayın.",
 "Mali başarı, sabır ve mükemmel malzemelerle başlar: İyi bir tarif gerekir.",
 "Zamanlama, yatırımlarınızın pişme süresidir: Doğru anı kollayın.",
 "Çeşitlendirme, finansal menüyü daha ilginç hale getirir: Farklı varlıklara yatırım yapın.",
 "Portföyünüzü seçerken, lezzetin yanı sıra riski de düşünün.",
 "Finansal hedeflerinizi tatlı bir başarıya dönüştürmek için doğru stratejiyi seçin."
            
]

pagination_idx = 0
menu_choice = "BIST_30" # 0, 1, 2, 3

BIST_30 = ["BIST_30"]
BIST_50 = ["BIST_50"]
BIST_100 = ["BIST_100"]
TAKIP_EDILEN = ["TAKIP_EDILEN"]
HEPSI = ["HEPSI"]

DATA = {"BIST_30": BIST_30,"BIST_50": BIST_50,  "BIST_100": BIST_100,"TAKIP_EDILEN":TAKIP_EDILEN,"HEPSI":HEPSI}

class UserRestriction:
    chat_id : int

    verified : bool

    restriction : str # BIST_30, BIST_50, BIST_100, ALL
    firstName : str
    lastName : str
    userName : str
    pagination_idx = 0 

    menu_choice = "BIST_30" 
    choices = []
    user_stock = [] # share_code : list
    createdTime : datetime



redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

api_url =  os.getenv('API_URL')

# controllers
user_db_create_url = api_url + "/user/db-create"
share_and_user_db_create_url = api_url + "/shareanduser/db-create" # 
share_db_create = api_url + "/share/db-create" # bu gereksiz olabilir.

share_and_user_db_delete = api_url + "/shareanduser/db-delete" #
share_and_user_me_follow_share = api_url + "/shareanduser/me-follow-share"


headers = {'Content-Type': 'application/json'}


def set_translation(stock_name, description):
    redis_client.set(stock_name, description)

    return description

def get_translations(stock_name, text):
    description = redis_client.get(stock_name)
    if description != None:
        description=redis_client.get(stock_name).decode('utf-8')
    
    if description is None:
        description = ts.translate_text(translator='google', query_text=text, to_language='tr')
        set_translation(stock_name, description)

    return description

def nple_array(array, count):
    subarrays = []
    # Iterate through the original array and split it into triple subarrays
    for i in range(0, len(array), count):
        subarray = array[i:i + count]
        subarrays.append(subarray)

    return subarrays


def read_stock_name(stocks):

    file = open(stocks[0], "r")
    text = file.read()
    for stock in text.split("\n"):
        stocks.append(stock)

    return stocks



BIST_30 = read_stock_name(BIST_30)
BIST_50 = read_stock_name(BIST_50)
BIST_100 = read_stock_name(BIST_100)
HEPSI = read_stock_name(HEPSI)
VERIFIED = False

choices = []
user_stock = []

def yahoo_info_bist(stock_name):
    ticker = yf.Ticker(stock_name+".IS") # BIST

    info = ticker.info

    long_name = info['longName'] if info.get('currentPrice') else ""

    stock_info = f"KOD: #{stock_name} \nADI:{long_name} \nGüncel Fiyat:{ info['currentPrice'] if info.get('currentPrice') else '' }TL \n\nFaaliyet:{get_translations(stock_name, info['longBusinessSummary']) if info.get('longBusinessSummary') else ''}"

    return stock_info

'''
# Yahoo finance graphs
data = yf.download(tickers='UBER', period='5d', interval='5m')
print(data)

#declare figure
fig = go.Figure()


#Candlestick
fig.add_trace(go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'], name = 'market data'))


# Add titles
fig.update_layout(
    title='Uber live share price evolution',
    yaxis_title='Stock Price (USD per Shares)')



# X-Axes
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=15, label="15m", step="minute", stepmode="backward"),
            dict(count=45, label="45m", step="minute", stepmode="backward"),
            dict(count=1, label="HTD", step="hour", stepmode="todate"),
            dict(count=3, label="3h", step="hour", stepmode="backward"),
            dict(step="all")
        ])

    )
)


fig.show()


'''

def main_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton( BIST_30[0] , callback_data="menu_" + BIST_30[0] ))
    keyboard.add(types.InlineKeyboardButton( BIST_50[0] , callback_data="menu_"+ BIST_50[0] ))
    keyboard.add(types.InlineKeyboardButton( TAKIP_EDILEN[0] , callback_data="menu_"+ TAKIP_EDILEN[0] ))
    keyboard.add(types.InlineKeyboardButton( BIST_100[0] , callback_data="menu_"+BIST_100[0] ))
    keyboard.add(types.InlineKeyboardButton( HEPSI[0] , callback_data="menu" + HEPSI[0] ))
    keyboard.add(types.InlineKeyboardButton( "Halka Arzlar" , callback_data="menu_PUBLICSOON" ))

    return keyboard



def add_continue_pagination(keyboard):
    keyboard.add(types.InlineKeyboardButton( "Hisseleri Görmeye Devam Et.", callback_data="continue_pagination" ))

    return keyboard

def add_settings_keyboard(keyboard, menu_choice):
    keyboard.add(types.InlineKeyboardButton( menu_choice +  " Hepsini Ekle", callback_data="add_all" ))
    keyboard.add(types.InlineKeyboardButton( menu_choice +  " Hepsini Sil", callback_data="remove_all" ))
    keyboard.add(types.InlineKeyboardButton( "Ana Menüye Dön", callback_data="main_menu" ))

    return keyboard


def build_keyboard_pagination(row_width, actives, i, menu_choice):

    keyboard = types.InlineKeyboardMarkup(row_width=row_width)

    order = 1
    for  stocks in nple_array(DATA[menu_choice][i*100+1:], row_width):
        buttons = []
        for j in range(row_width):
            
            actives = [value for value in actives if value >= ( 100 * (i) ) and value <= ( 100 * (i+1) )]
            item = ( order + (100 * i) ) 
            if (item in actives):
                if j < len(stocks) and stocks[j] != None and stocks[j] != '':
                    buttons.append(types.InlineKeyboardButton(str(order)+ "." + stocks[j] + "✅", callback_data = stocks[j]))
            else:
                if j < len(stocks) and stocks[j] != None and stocks[j] != '':
                    buttons.append(types.InlineKeyboardButton(str(order)+ "." + stocks[j], callback_data = stocks[j]))
            order += 1
        keyboard.add(*buttons)

    add_settings_keyboard(keyboard, menu_choice)

    return keyboard

def build_keyboard_follow(keyboard, row_width, stocks, menu_choice):

    keyboard.add(types.InlineKeyboardButton( "Ana Menüye Dön", callback_data="main_menu" ))

    return keyboard

def build_keyboard(row_width, actives, menu_choice):

    keyboard = types.InlineKeyboardMarkup(row_width=row_width)



    order = 1
    for  stocks in nple_array(DATA[menu_choice][1:], row_width):
        buttons = []
        for i in range(row_width):
            
            if (order in actives):
                if i < len(stocks) and stocks[i] != None and stocks[i] != '':
                    buttons.append(types.InlineKeyboardButton(str(order)+ "." + stocks[i] + "✅", callback_data=stocks[i]))
            else:
                if i < len(stocks) and stocks[i] != None and stocks[i] != '':
                    buttons.append(types.InlineKeyboardButton(str(order)+ "." + stocks[i], callback_data=stocks[i]))
            order += 1
        keyboard.add(*buttons)

    add_settings_keyboard(keyboard, menu_choice)
    
    return keyboard

def confirmation_keyboard(type, menu_choice):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton( menu_choice +  " Evet", callback_data=type+"_yes" ), types.InlineKeyboardButton( menu_choice +  " Hayır", callback_data=type+"_no" ))
    return keyboard


# keyboard.add(button_foo,button_1)
# keyboard.add(button_bar,button_2)

# bot.send_message("12345", text='Keyboard example', reply_markup=keyboard)

# Define a handler for the '/start' command
@bot.message_handler(commands=['start'])
def handle_start(message):
    # global VERIFIED
    #redis_client.delete(message.chat.id)
    userRestriction = redis_client.get(message.chat.id)
    
    if userRestriction is None:

        query_params = {'chatId': message.chat.id}
        response = requests.get(share_and_user_me_follow_share, params=query_params)
        if response.status_code == 200 :
            stock_list = json.loads(response.text)

            if len(stock_list) == 0:
                bot.send_message(message.chat.id, "Merhaba Ben Gurme Finans Garson Bot Sizi Yönlendireceğim Lütfen Dekont Numaranızı Girin. ")
                userRestriction = UserRestriction()
                userRestriction.createdTime = datetime.now()
                userRestriction.verified = False
                userRestriction.chat_id = message.chat.id
                userRestriction.firstName = message.chat.first_name
                userRestriction.lastName = message.chat.last_name
                userRestriction.userName = message.from_user.username
                redis_client.set( message.chat.id, pickle.dumps(userRestriction) )
        
            else:
                userRestriction = sync_redis(userRestriction, message.chat.id)
                if userRestriction.verified:
                    keyboard = main_menu_keyboard()

                    # Send a welcome message to the user
                    bot.send_message(message.chat.id, '''
                        Merhaba Ben Gurme Finans Garson Bot
                        Sizlere görmek istediğiniz sinyal ile ilgili yardımcı olacağım.
                        Aşağıdaki menüden görmek istediğiniz sinyalleri seçebilirsiniz.
                        MENU
                        KOD ADI ~ AÇIKLAMA
                        BIST30 : Gelen sinyaller içerisinden sadece BIST30 olan sinyalleri şeçin veya çıkarın.
                        BIST100 : Gelen sinyaller içerisinden sadece BIST100 olan sinyalleri seçin veya çıkarın.
                        TAKIP_EDILEN : Gelen sinyaller içerisinden seçmiş olduklarınızı görüntüleyin veya çıkarın.
                        HEPSİ : Gelen sinyallerin hepsini seçin veya çıkarın.


                        Not: Menüde seçmek isteğiniz özelliklerin kod adını geri dönüş yapmanız yeterli.'''
                    , reply_markup=keyboard)

                else:
                    bot.send_message(message.chat.id, "Merhaba Ben Gurme Finans Garson Bot Sizi Yönlendireceğim Lütfen Dekont Numaranızı Girin. ")
        

        #aa = redis_client.get(message.chat.id)
        #deneme2 = pickle.loads(aa)
        # print("")

    else:
        userRestriction = pickle.loads(userRestriction)
        userRestriction = sync_redis(userRestriction, message.chat.id)
        if userRestriction.verified:
            keyboard = main_menu_keyboard()

            # Send a welcome message to the user
            bot.send_message(message.chat.id, '''
                Merhaba Ben Gurme Finans Garson Bot
                Sizlere görmek istediğiniz sinyal ile ilgili yardımcı olacağım.
                Aşağıdaki menüden görmek istediğiniz sinyalleri seçebilirsiniz.
                MENU
                KOD ADI ~ AÇIKLAMA
                BIST30 : Gelen sinyaller içerisinden sadece BIST30 olan sinyalleri şeçin veya çıkarın.
                BIST100 : Gelen sinyaller içerisinden sadece BIST100 olan sinyalleri seçin veya çıkarın.
                TAKIP_EDILEN : Gelen sinyaller içerisinden seçmiş olduklarınızı görüntüleyin veya çıkarın.
                HEPSİ : Gelen sinyallerin hepsini seçin veya çıkarın.


                Not: Menüde seçmek isteğiniz özelliklerin kod adını geri dönüş yapmanız yeterli.'''
            , reply_markup=keyboard)

        else:
            bot.send_message(message.chat.id, "Merhaba Ben Gurme Finans Garson Bot Sizi Yönlendireceğim Lütfen Dekont Numaranızı Girin. ")


# Define a handler for incoming text messages
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # global VERIFIED
    # Echo the received message
    #if not message.html_text.startswith("/"):
    userRestriction = redis_client.get(message.chat.id)
    userRestriction = pickle.loads(userRestriction)

    if userRestriction is not None:
        url = api_url + '/airtable/pay-verification'
        query_params = {'dekontNo': message.text}

        # Send a POST request with the specified URL and query parameters
        response = requests.post(url, params=query_params)
        response_json = response.json()
        if ( response_json["isOk"] == True ):
            userRestriction.verified = True

            data = {"name": (userRestriction.firstName if userRestriction.firstName else "" ) , "lastName": (userRestriction.lastName if userRestriction.lastName else "" ), "userName": (userRestriction.userName if userRestriction.userName else ""), "chatId": str(userRestriction.chat_id) }
            response = requests.post ( url = user_db_create_url, data = json.dumps(data) ,  headers=headers)

            redis_client.set(message.chat.id, pickle.dumps(userRestriction))

            keyboard = main_menu_keyboard()
            bot.send_message( message.chat.id, response_json['message'] )
            bot.send_message( message.chat.id, "Vip Linkiniz: " + response_json['telegramVIPLink'] )
            bot.send_message( message.chat.id, "Destek Linkiniz: " + response_json['telegramDestekChannelLink'] )
            bot.send_message( message.chat.id, "Bist 30 Linkiniz: " + response_json['telegramBIST30Link'] )

            
            # Send a welcome message to the user
            bot.send_message(message.chat.id, '''
                Merhaba Ben Gurme Finans Garson Bot
                Sizlere görmek istediğiniz sinyal ile ilgili yardımcı olacağım.
                Aşağıdaki menüden görmek istediğiniz sinyalleri seçebilirsiniz.
                MENU
                KOD ADI ~ AÇIKLAMA
                BIST30 : Gelen sinyaller içerisinden sadece BIST30 olan sinyalleri şeçin.
                BIST50 : Gelen sinyaller içerisinden sadece BIST50 olan sinyalleri şeçin.
                BIST100 : Gelen sinyaller içerisinden sadece BIST100 olan sinyalleri seçin.
                ÖZEL : Gelen sinyaller içerisinden seçmiş olduklarınızı görüntüleyin.
                HEPSİ : Gelen sinyallerin hepsini seçin.


                Not: Menüde seçmek isteğiniz özelliklerin kod adını geri dönüş yapmanız yeterli.'''
            , reply_markup=keyboard)
        else:
            bot.send_message( message.chat.id, response_json['message'] )

  



# TELEGRAM BOT
# @bot.message_handler(commands=['Greet'])
# def greeting(message):
#    keyboard = build_keyboard(3, [])
#    bot.reply_to(message, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

def sync_redis(userRestriction, chat_id):
    if ( userRestriction is not None) :
        query_params = {'chatId': chat_id}

        # Send a POST request with the specified URL and query parameters
        
        response = requests.get(share_and_user_me_follow_share, params=query_params)
        stock_list = json.loads(response.text)
        
        choice_list = []
        for stock in stock_list:
            stock_index = HEPSI.index(stock)
            choice_list.append(stock_index)

        userRestriction.choices = sorted(choice_list if choice_list else [])
        userRestriction.user_stock = stock_list 
        redis_client.set(chat_id, pickle.dumps(userRestriction))

        return userRestriction
    
    else:
        return None




@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    #choice
    # menu_choice
    # global user_stock
    # global pagination_idx

    userRestriction = redis_client.get(call.from_user.id)
    userRestriction = pickle.loads(userRestriction)
    

    random_element = random.choice(motivation)

    bot.answer_callback_query(call.id, random_element)
    if ('main_menu' == call.data):
        userRestriction.pagination_idx = 0
        userRestriction = sync_redis(userRestriction, call.from_user.id)

        handle_start(call.message)
    elif('menu' in call.data):
        if(BIST_30[0] in call.data):
            userRestriction.menu_choice = BIST_30[0]
            userRestriction.choices = [BIST_30.index(choice) if choice in BIST_30 else None for choice in userRestriction.user_stock ]
            userRestriction.choices = [x for x in userRestriction.choices if x is not None]


            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

            data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock }
            response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)
            
            
            keyboard = build_keyboard(3, userRestriction.choices, userRestriction.menu_choice)
            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

        elif(BIST_50[0] in call.data):
            userRestriction.menu_choice = BIST_50[0]
            userRestriction.choices = [BIST_50.index(choice) if choice in BIST_50 else None for choice in userRestriction.user_stock ]
            userRestriction.choices =  [x for x in userRestriction.choices if x is not None]
            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))
            
            data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock }
            response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)
            

            keyboard = build_keyboard(3, userRestriction.choices, userRestriction.menu_choice)
            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

        elif(BIST_100[0] in call.data):
            userRestriction.menu_choice = BIST_100[0]
            keyboard = build_keyboard(3, userRestriction.choices, userRestriction.menu_choice)
            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

            data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock }
            response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)
            

            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

            keyboard = types.InlineKeyboardMarkup()
            add_settings_keyboard(keyboard, userRestriction.menu_choice)
            bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)


        elif(HEPSI[0] in call.data):
            userRestriction.menu_choice = HEPSI[0]
            keyboard = build_keyboard_pagination(3, userRestriction.choices, userRestriction.pagination_idx, userRestriction.menu_choice)
            
            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

            data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock }
            response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)
            

            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard = add_continue_pagination(keyboard)
            add_settings_keyboard(keyboard, userRestriction.menu_choice)

            bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)


        elif(TAKIP_EDILEN[0] in call.data):
            userRestriction.menu_choice = TAKIP_EDILEN[0]
            #keyboard = build_keyboard(3, [], userRestriction.menu_choice)
            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))
            #DATA[TAKIP_EDILEN[0]] = [TAKIP_EDILEN[0]] + userRestriction.user_stock # sonradan bu da redise gömülecek en azından seçilen kısmı

            # bot.send_message(call.message.chat.id, userRestriction.user_stock)
            keyboard = types.InlineKeyboardMarkup(row_width=3)

            keyboard = build_keyboard_follow( keyboard, 3, userRestriction.user_stock, userRestriction.menu_choice)
            bot.send_message(call.message.chat.id, str(userRestriction.user_stock))
            bot.send_message(call.message.chat.id, "Hisselerinizi seçmeye devam edin." , reply_markup=keyboard)


            data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock }
            response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)
            

        else:
            bot.send_message(call.message.chat.id, "Halka Arzlar Pek Yakında.\n\n")




    #if menu_choice == BIST_30[0]:
    if call.data in DATA[userRestriction.menu_choice]:
        index = DATA[userRestriction.menu_choice].index(call.data)
        if index not in userRestriction.choices:
            userRestriction.choices.append(index)
            userRestriction.user_stock.append(call.data)
            
            if userRestriction.menu_choice == HEPSI[0] :
                keyboard = build_keyboard_pagination(3, userRestriction.choices, userRestriction.pagination_idx, userRestriction.menu_choice)
            else:
                keyboard=build_keyboard(3,userRestriction.choices, userRestriction.menu_choice)

            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

            data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock }
            response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)
            
            
            bot.send_message(call.message.chat.id, DATA[userRestriction.menu_choice][index] + " şeçtiniz.\n\n" + yahoo_info_bist(DATA[userRestriction.menu_choice][index]), reply_markup=keyboard)
            keyboard = types.InlineKeyboardMarkup()
            if userRestriction.menu_choice == BIST_100[0]:
                keyboard=add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

            if userRestriction.menu_choice == HEPSI[0]:
                keyboard= add_continue_pagination(keyboard)
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)
            
        else:
            userRestriction.choices.remove(index)
            userRestriction.user_stock.remove(call.data) if call.data in userRestriction.user_stock else userRestriction.user_stock
            
            
            if userRestriction.menu_choice == HEPSI[0] :
                keyboard = build_keyboard_pagination(3, userRestriction.choices, userRestriction.pagination_idx, userRestriction.menu_choice)
            else:
                keyboard=build_keyboard(3, userRestriction.choices, userRestriction.menu_choice)
            
            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

            data = {"chatId": str(userRestriction.chat_id) , "shareCode": [call.data] }
            response = requests.delete ( url = share_and_user_db_delete, data = json.dumps(data) ,  headers=headers)
            
            
            bot.send_message(call.message.chat.id, DATA[userRestriction.menu_choice][index] + " kaldırıldı\n", reply_markup=keyboard)

            keyboard = types.InlineKeyboardMarkup()
            if userRestriction.menu_choice == BIST_100[0]:
                add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

            if userRestriction.menu_choice == HEPSI[0]:
                keyboard = add_continue_pagination(keyboard)
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

    elif call.data == 'add_all':
        keyboard = confirmation_keyboard('add_all', userRestriction.menu_choice)
        bot.send_message(call.message.chat.id, "Tüm " +  " Hisselerini Eklemek için emin misiniz?", reply_markup=keyboard)


    elif call.data == 'remove_all':
        keyboard = confirmation_keyboard('remove_all', userRestriction.menu_choice)
        bot.send_message(call.message.chat.id, "Tüm " +  " Hisselerini Silmek için emin misiniz?", reply_markup=keyboard)


    elif call.data == 'add_all_yes':
        if userRestriction.menu_choice == DATA[userRestriction.menu_choice][0]:
            if userRestriction.menu_choice == HEPSI[0]:
                userRestriction.choices = list(range(1,101))
                set_user_stock = set(userRestriction.user_stock)
                set_user_stock = set_user_stock.union(set(DATA[userRestriction.menu_choice][100*userRestriction.pagination_idx+1:100*userRestriction.pagination_idx+1+100]))
                userRestriction.user_stock = list(set_user_stock)
            else:
                userRestriction.choices = list(range(1,len(DATA[userRestriction.menu_choice])))
                set_user_stock = set(userRestriction.user_stock)
                set_user_stock = set_user_stock.union(set(DATA[userRestriction.menu_choice][1:]))
                userRestriction.user_stock = list(set_user_stock)

            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

            data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock[1:] }
            response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)
            
            if userRestriction.menu_choice == HEPSI[0] :
                keyboard = build_keyboard_pagination(3, userRestriction.choices, userRestriction.pagination_idx, userRestriction.menu_choice)
            else:
                keyboard = build_keyboard(3,userRestriction.choices, userRestriction.menu_choice)
            bot.send_message(call.message.chat.id, DATA[userRestriction.menu_choice][0] + " hepsini seçtiniz.\n\n", reply_markup=keyboard)

            if userRestriction.menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

            if userRestriction.menu_choice == HEPSI[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_continue_pagination(keyboard)            
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)
            

    elif call.data == 'add_all_no':
        if userRestriction.menu_choice == DATA[userRestriction.menu_choice][0]:
            
            if userRestriction.menu_choice == HEPSI[0] :
                keyboard = build_keyboard_pagination(3, userRestriction.choices, userRestriction.pagination_idx, userRestriction.menu_choice)
            else:
                keyboard=build_keyboard(3,userRestriction.choices, userRestriction.menu_choice)
            
            bot.send_message(call.message.chat.id, DATA[userRestriction.menu_choice][0] + " Sofranız hazır.\n\n", reply_markup=keyboard)
            if userRestriction.menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)



    elif call.data == 'remove_all_yes':
        if userRestriction.menu_choice == DATA[userRestriction.menu_choice][0]:
            userRestriction.choices = []

            set_user_stock = set(userRestriction.user_stock)
            userRestriction.user_stock = list(set_user_stock.difference(set(DATA[userRestriction.menu_choice][1:])))

            redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

            code = list(set(DATA[userRestriction.menu_choice][1:]))

            data = {"chatId": str(userRestriction.chat_id) , "shareCode": code[1:] } # 5956951460
            response = requests.delete( url = share_and_user_db_delete, data = json.dumps(data) ,  headers=headers)
            
            if userRestriction.menu_choice == HEPSI[0] :
                keyboard = build_keyboard_pagination(3, userRestriction.choices, userRestriction.pagination_idx, userRestriction.menu_choice)
            else:
                keyboard=build_keyboard(3, userRestriction.choices, userRestriction.menu_choice)
            bot.send_message(call.message.chat.id, DATA[userRestriction.menu_choice][0] + " hepsini sildiniz.\n\n", reply_markup=keyboard)

            if userRestriction.menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)
            if userRestriction.menu_choice == HEPSI[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_continue_pagination(keyboard)
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)


    elif call.data == 'remove_all_no':
        if userRestriction.menu_choice == DATA[userRestriction.menu_choice][0]:
            
            if userRestriction.menu_choice == HEPSI[0] :
                keyboard = build_keyboard_pagination(3, userRestriction.choices, userRestriction.pagination_idx, userRestriction.menu_choice)
            else:
                keyboard=build_keyboard(3, userRestriction.choices, userRestriction.menu_choice)
            
            
            bot.send_message(call.message.chat.id, DATA[userRestriction.menu_choice][0] + " sofranız hazır.\n\n", reply_markup=keyboard)

            if userRestriction.menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard, userRestriction.menu_choice)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

    elif call.data == 'continue_pagination':
        userRestriction.pagination_idx += 1
        # userRestriction.choices = []
        redis_client.set(call.from_user.id, pickle.dumps(userRestriction))

        data = {"chatId": str(userRestriction.chat_id) , "shareCode": userRestriction.user_stock }
        response = requests.post ( url = share_and_user_db_create_url, data = json.dumps(data) ,  headers=headers)


        call.data = 'menu' + HEPSI[0]
        handle_button_press(call)

    else :
        print ("Unknown")


bot.polling()

