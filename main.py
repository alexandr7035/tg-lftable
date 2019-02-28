#!./lftable-venv/bin/python3
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode

import urllib.request
from datetime import datetime

import pytz
import os


# If there's no 'tokens' directory.
if not os.path.exists('tokens/'):
    print("You should create 'tokens/' dir and put 'token.dev' or 'token.release' file there. Exit")
    exit()


# Used for refresh function
global old_ttb


############################# Timetables #########################################

# Class for storing timetable's options.
class TTBS():
    pass

pravo_c1 = TTBS()
pravo_c2 = TTBS()
pravo_c3 = TTBS()
pravo_c4 = TTBS()

pravo_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_1_pravo.xls'
pravo_c1.name = 'Правоведение, 1-й курс'

pravo_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_2_pravo.xls'
pravo_c2.name = 'Правоведение, 2-й курс'

pravo_c3.url = 'https://law.bsu.by/pub/2/Raspisanie_3_pravo.xls'
pravo_c3.name = 'Правоведение, 3-й курс'

pravo_c4.url = 'https://law.bsu.by/pub/2/Raspisanie_4_pravo.xls'
pravo_c4.name = 'Правоведение, 4-й курс'


# Get timetable's mtime using urllib module. 
def ttb_gettime(ttb):
    
    response =  urllib.request.urlopen(ttb.url)
    
    # Get date from HTTP header.
    native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
    
    # Transfer date to normal format.
    gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')
    
    # Transfer date to our timezone (GMT+3).
    old_tz = pytz.timezone('Europe/London')
    new_tz = pytz.timezone('Europe/Minsk')
    
    date = old_tz.localize(gmt_date).astimezone(new_tz) 
    
    return(date)
                                                



############################### Bot ############################################

# /start command --> calls main menu.
def start(bot, update):
    update.message.reply_text(main_menu_message(), parse_mode=ParseMode.HTML,
                           reply_markup=main_menu_keyboard())


def menu_actions(bot, update):
    query = update.callback_query
    
    global current_callback
    current_callback = query.data
    
    print('Button pressed: ', current_callback)
    
    # Calls main menu.
    if query.data == 'main_menu':

        bot.edit_message_text(chat_id = query.message.chat_id,
            message_id = query.message.message_id,
            text=main_menu_message(),
            # Used for bold font
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard())

    
    # Calls answer with certain timetable depending on the button pressed before.
    if query.data in  ['answer_p1', 'answer_p2', 'answer_p3', 'answer_p4', 'refresh']:

        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=answer_message(),
                        # Used for bold font
                        parse_mode=ParseMode.HTML,
                        reply_markup=answer_keyboard())
    



############################# Messages #########################################

# Main menu text
def main_menu_message():
  
    menu_text = '<b>LFTable</b>: работа с расписанием занятий юридического факультета БГУ.\n\n'
    
    menu_text += 'Источник: https://law.bsu.by\n'
    menu_text += 'Информация об авторских правах юрфака: https://law.bsu.by/avtorskie-prava.html\n\n'
  
    menu_text += 'Выберите нужное расписание:'
    return(menu_text)


# The message text is formed in accordance with the timetable selected in the main menu.
def answer_message():
    
    # Used for refresh function
    global old_ttb
    
    if current_callback == 'answer_p1':
        current_ttb = pravo_c1
    elif current_callback == 'answer_p2':
        current_ttb = pravo_c2
    elif current_callback == 'answer_p3':
        current_ttb = pravo_c3
    elif current_callback == 'answer_p4':
        current_ttb = pravo_c4
    elif current_callback == 'refresh':
        current_ttb = old_ttb
    
        
    # Get the timetable's "mtime"
    ttb_datetime = ttb_gettime(current_ttb)
    
    
    # Change date to necessary format.
    update_time = ttb_datetime.strftime('%H:%M')
    update_date = ttb_datetime.strftime('%d.%m.%Y')
    
    
    # Form the message's text
    answer_text = '<b>' + current_ttb.name + '</b>\n\n'
    
    answer_text += 'Дата обновления: ' + update_date + '\n'
    answer_text += 'Время обновления: '+ update_time + '\n\n'

    answer_text += '<b>СКАЧАТЬ</b>: ' + current_ttb.url
    

    
    # For 'refresh' function.
    old_ttb = current_ttb
    
    
    # Return this text
    return(answer_text)
    
    
    
############################ Keyboards #########################################

# Main menu keyboard.
# 4 buttons in main menu. Each button is designed for the corresponding timetable (1-4 course)
def main_menu_keyboard():
    
    pravo_c1.btn = InlineKeyboardButton('Правоведение - 1⃣', callback_data='answer_p1')
    pravo_c2.btn = InlineKeyboardButton('Правоведение - 2⃣', callback_data='answer_p2')
    pravo_c3.btn = InlineKeyboardButton('Правоведение - 3⃣', callback_data='answer_p3')
    pravo_c4.btn = InlineKeyboardButton('Правоведение - 4⃣', callback_data='answer_p4')

    
    keyboard = [[pravo_c1.btn],
                [pravo_c2.btn],
                [pravo_c3.btn],
                [pravo_c4.btn]]            
              
    return(InlineKeyboardMarkup(keyboard))


# Menu for specific timetable. One button returns to main menu, one refreshes date and time info.
def answer_keyboard():
    
    # Button to refresh current answer menu (so you don't have to come back to main menu).
    refresh_button = InlineKeyboardButton('🔄 Обновить   ', callback_data='refresh')
    # Sends you back to the main menu.
    back_button = InlineKeyboardButton('⬅️ Назад в меню', callback_data='main_menu')

    keyboard = [[refresh_button],
                  [back_button]]
                  
    return(InlineKeyboardMarkup(keyboard))



############################# Bot settings #########################################

# Use dev token
token_to_use = 'token.dev'
#token_to_use = 'token.release'

try:
    token_file = open('tokens/' + token_to_use) 
except Exception:
    print("No token file \'" + token_to_use + "\'. You should put it into 'tokens/' dir. Exit.")
    exit()


# Read token
token_str = token_file.readline()[:-1] 
token_file.close()

updater = Updater(token_str)

dp = updater.dispatcher


# Handlers
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CallbackQueryHandler(menu_actions))



# Checking for updates.
updater.start_polling(clean=True)
# Stop bot if  <Ctrl + C> pressed.
updater.idle()
