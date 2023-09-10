import os 
import telebot

import random

# send graph to telebot 
import numpy as np
import pandas as pd


import redis

import yfinance as yf
import plotly

import plotly.graph_objs as go
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
SPECIAL= ["SECILEN"]
HEPSI = ["HEPSI"]

DATA = {"BIST_30": BIST_30,"BIST_50": BIST_50,  "BIST_100": BIST_100,"SPECIAL":SPECIAL,"HEPSI":HEPSI}


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

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

choices = []
user_stock = []

def yahoo_info_bist(stock_name):
    ticker = yf.Ticker(stock_name+".IS") # BIST

    info = ticker.info

    long_name = info['longName']

    stock_info = f"KOD: #{stock_name} \nADI:{long_name} \nGüncel Fiyat:{info['currentPrice']}TL \n\nFaaliyet:{get_translations(stock_name, info['longBusinessSummary'])}"

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
    keyboard.add(types.InlineKeyboardButton( BIST_100[0] , callback_data="menu_"+BIST_100[0] ))
    keyboard.add(types.InlineKeyboardButton( HEPSI[0] , callback_data="menu" + HEPSI[0] ))
    keyboard.add(types.InlineKeyboardButton( "Halka Arzlar" , callback_data="menu_PUBLICSOON" ))

    return keyboard


def add_continue_pagination(keyboard):
    keyboard.add(types.InlineKeyboardButton( "Hisseleri Görmeye Devam Et.", callback_data="continue_pagination" ))

    return keyboard

def add_settings_keyboard(keyboard):
    keyboard.add(types.InlineKeyboardButton( menu_choice +  " Hepsini Ekle", callback_data="add_all" ))
    keyboard.add(types.InlineKeyboardButton( menu_choice +  " Hepsini Sil", callback_data="remove_all" ))
    keyboard.add(types.InlineKeyboardButton( "Ana Menüye Dön", callback_data="main_menu" ))

    return keyboard


def build_keyboard_pagination(row_width, actives, i):

    keyboard = types.InlineKeyboardMarkup(row_width=row_width)

    order = 1
    for  stocks in nple_array(DATA[menu_choice][i*100+1:], row_width):
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

    add_settings_keyboard(keyboard)

    return keyboard


def build_keyboard(row_width, actives):

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

    add_settings_keyboard(keyboard)

    return keyboard

def confirmation_keyboard(type):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton( menu_choice +  " Evet", callback_data=type+"_yes" ), types.InlineKeyboardButton( menu_choice +  " Hayır", callback_data=type+"_no" ))
    return keyboard


# keyboard.add(button_foo,button_1)
# keyboard.add(button_bar,button_2)

# bot.send_message("12345", text='Keyboard example', reply_markup=keyboard)


# Define a handler for the '/start' command
@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = main_menu_keyboard()

    # Send a welcome message to the user
    bot.send_message(message.chat.id, '''
        Merhaba Ben Gurme Finans Garson Bot
        Sizlere görmek istediğiniz sinyal ile ilgili yardımcı olacağım.
        Aşağıdaki menüden görmek istediğiniz sinyalleri seçebilirsiniz.
        MENU
        KOD ADI ~ AÇIKLAMA
        BIST30 : Gelen sinyaller içerisinden sadece BIST30 olan sinyalleri şeçin.
        BIST100 : Gelen sinyaller içerisinden sadece BIST100 olan sinyalleri seçin.
        ÖZEL : Gelen sinyaller içerisinden seçmiş olduklarınızı görüntüleyin.
        HEPSİ : Gelen sinyallerin hepsini seçin.


        Not: Menüde seçmek isteğiniz özelliklerin kod adını geri dönüş yapmanız yeterli.'''
    ,reply_markup=keyboard)




# TELEGRAM BOT
@bot.message_handler(commands=['Greet'])
def greeting(message):
    keyboard = build_keyboard(3, [])
    bot.reply_to(message, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_press(call):
    global choices 
    global menu_choice
    global user_stock
    global pagination_idx

    random_element = random.choice(motivation)

    bot.answer_callback_query(call.id, random_element)
    if ('main_menu' == call.data):
        handle_start(call.message)
    elif('menu' in call.data):
        if(BIST_30[0] in call.data):
            menu_choice = BIST_30[0]
            choices = [BIST_30.index(choice) if choice in BIST_30 else None for choice in user_stock ]
            choices = [x for x in choices if x is not None]
            keyboard = build_keyboard(3, choices)
            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

        elif(BIST_50[0] in call.data):
            menu_choice = BIST_50[0]
            choices = [BIST_50.index(choice) if choice in BIST_50 else None for choice in user_stock ]
            choices =  [x for x in choices if x is not None]
            keyboard = build_keyboard(3, choices)
            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

        elif(BIST_100[0] in call.data):
            menu_choice = BIST_100[0]
            keyboard = build_keyboard(3, choices)
            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

            keyboard = types.InlineKeyboardMarkup()
            add_settings_keyboard(keyboard)
            bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)


        elif(HEPSI[0] in call.data):
            menu_choice = HEPSI[0]
            keyboard = build_keyboard_pagination(3, choices, pagination_idx)
            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)
            
            keyboard = types.InlineKeyboardMarkup()
            add_continue_pagination(keyboard)
            add_settings_keyboard(keyboard)

            bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)


        elif(SPECIAL[0] in call.data):
            menu_choice = SPECIAL[0]
            keyboard = build_keyboard(3, [])
            bot.send_message(call.message.chat.id, "Hadi lokma lokma hisselerinizi seçin. ", reply_markup=keyboard)

        else:
            bot.send_message(call.message.chat.id, "Halka Arzlar Pek Yakında.\n\n")




    #if menu_choice == BIST_30[0]:
    if call.data in DATA[menu_choice]:
        index = DATA[menu_choice].index(call.data)
        if index not in choices:
            choices.append(index)
            user_stock.append(call.data)
            keyboard=build_keyboard(3,choices)
            bot.send_message(call.message.chat.id, DATA[menu_choice][index] + " şeçtiniz.\n\n" + yahoo_info_bist(DATA[menu_choice][index]), reply_markup=keyboard)
            keyboard = types.InlineKeyboardMarkup()
            if menu_choice == BIST_100[0]:
                keyboard=add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

            if menu_choice == HEPSI[0]:
                keyboard= add_continue_pagination(keyboard)
                keyboard = add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)
            
        else:
            choices.remove(index)
            user_stock.remove(call.data) if call.data in user_stock else user_stock
            keyboard=build_keyboard(3,choices)
            bot.send_message(call.message.chat.id, DATA[menu_choice][index] + " kaldırıldı\n", reply_markup=keyboard)

            keyboard = types.InlineKeyboardMarkup()
            if menu_choice == BIST_100[0]:
                add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

            if menu_choice == HEPSI[0]:
                keyboard = add_continue_pagination(keyboard)
                keyboard = add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

    elif call.data == 'add_all':
        keyboard = confirmation_keyboard('add_all')
        bot.send_message(call.message.chat.id, "Tüm " +  " Hisselerini Eklemek için emin misiniz?", reply_markup=keyboard)


    elif call.data == 'remove_all':
        keyboard = confirmation_keyboard('remove_all')
        bot.send_message(call.message.chat.id, "Tüm " +  " Hisselerini Silmek için emin misiniz?", reply_markup=keyboard)


    elif call.data == 'add_all_yes':
        if menu_choice == DATA[menu_choice][0]:
            if menu_choice == HEPSI[0]:
                choices = list(range(1,101))
                set_user_stock = set(user_stock)
                set_user_stock = set_user_stock.union(set(DATA[menu_choice][100*pagination_idx+1:100*pagination_idx+1+100]))
                user_stock = list(set_user_stock)
            else:
                choices = list(range(1,len(DATA[menu_choice])))
                set_user_stock = set(user_stock)
                set_user_stock = set_user_stock.union(set(DATA[menu_choice][1:]))
                user_stock = list(set_user_stock)

            keyboard=build_keyboard(3,choices)
            bot.send_message(call.message.chat.id, DATA[menu_choice][0] + " hepsini seçtiniz.\n\n", reply_markup=keyboard)

            if menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

            if menu_choice == HEPSI[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_continue_pagination(keyboard)            
                keyboard = add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)
            

    elif call.data == 'add_all_no':
        if menu_choice == DATA[menu_choice][0]:
            keyboard=build_keyboard(3,choices)
            bot.send_message(call.message.chat.id, DATA[menu_choice][0] + " Sofranız hazır.\n\n", reply_markup=keyboard)
            if menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)



    elif call.data == 'remove_all_yes':
        if menu_choice == DATA[menu_choice][0]:
            choices = []

            set_user_stock = set(user_stock)
            user_stock = list(set_user_stock.difference(set(DATA[menu_choice][1:])))

            keyboard=build_keyboard(3,choices)
            bot.send_message(call.message.chat.id, DATA[menu_choice][0] + " hepsini sildiniz.\n\n", reply_markup=keyboard)

            if menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)


    elif call.data == 'remove_all_no':
        if menu_choice == DATA[menu_choice][0]:
            keyboard=build_keyboard(3,choices)
            bot.send_message(call.message.chat.id, DATA[menu_choice][0] + " sofranız hazır.\n\n", reply_markup=keyboard)

            if menu_choice == BIST_100[0]:
                keyboard = types.InlineKeyboardMarkup()
                keyboard = add_settings_keyboard(keyboard)
                bot.send_message(call.message.chat.id, "Sofranız hazır mı?.\n\n", reply_markup=keyboard)

    elif call.data == 'continue_pagination':
        pagination_idx+=1
        choices = []
        call.data = 'menu'+HEPSI[0]
        handle_button_press(call)

    else :
        print ("Unknown")


bot.polling()
