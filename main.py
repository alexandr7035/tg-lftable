#!./lftable-venv/bin/python3 -B
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode

import urllib.request
from datetime import datetime

import pytz
import os
import sys

import logging
import sqlite3

import time

# See static.py to understant how it works.
# This file contains TTBS objects, their attributes, paths to databases and token files. 
from static import *


# Logging settings. Log all exceptions.
logging.basicConfig(filename="lftable.log", level=logging.INFO)
logger = logging.getLogger('mylogger')

# Install exception handler
def my_handler(type, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))
sys.excepthook = my_handler



# If there's no 'tokens' directory.
if not os.path.exists('tokens/'):
    print("You should create 'tokens/' dir and put 'token.dev' or 'token.release' file there. Exit")
    exit()


# Used for refresh function
old_ttb = None
# Used for notify function
notify_status = None
current_ttb = None


# Create necessary project dirs and files.
# (See 'static.py' for values of the variables)
def first_run_check():
    
    try:
        os.mkdir(db_dir)
    except Exception:
        pass
        
    try:
        os.mkdir(tokens_dir)
    except Exception:
        pass  
    
 
    if not os.path.exists(users_db):
        conn = sqlite3.connect(users_db)
        cursor = conn.cursor()
        
        
        for table_name in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4']:
            cursor.execute('CREATE TABLE ' + table_name + ' (users)')
            
        conn.commit()
        conn.close()
        
    
    if not os.path.exists(times_db):
        
        conn = sqlite3.connect(times_db)
        cursor = conn.cursor()
        
        cursor.execute('CREATE TABLE times (ttb, time)')
        conn.commit()
        
        for ttb in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4']:
            cursor.execute('INSERT INTO times VALUES ("' + ttb + '", "")')
        
        conn.commit()
        conn.close()
        
# Sets times to the 'times.db' immediately after the run WITHOUT notifiying users 
# Prevents late notifications if the program was down for a long time.
def db_set_times_after_run():
    conn = sqlite3.connect(times_db)
    cursor = conn.cursor()
    
    for ttb in [pravo_c1, pravo_c2, pravo_c3, pravo_c4]:
        
        update_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        print(update_time)
        
        cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (ttb.shortname,));
        
    conn.commit()
    conn.close()


db_set_times_after_run()
first_run_check()




############################# Timetables #########################################




# Get timetable's mtime using urllib module. 
def ttb_gettime(ttb):
    
    response =  urllib.request.urlopen(ttb.url, timeout=25)
    
    # Get date from HTTP header.
    native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
    
    # Transfer date to normal format.
    gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')
    
    # Transfer date to our timezone (GMT+3).
    old_tz = pytz.timezone('Europe/London')
    new_tz = pytz.timezone('Europe/Minsk')
    
    date = old_tz.localize(gmt_date).astimezone(new_tz) 
    
    return(date)
                                                

# Checks if user is notified when timetable is updated.
# Used to set text on the "notify" button.
def check_user_notified(ttb, user_id):
    
    # Connect to users db.
    conn = sqlite3.connect(users_db)
    cursor = conn.cursor()
        
    cursor.execute('SELECT users FROM ' + ttb.shortname)
    result = cursor.fetchall()
        
    conn.close()
    
    # List for users notifed about current ttb updates.
    users_to_notify = []
    for i in result:
       users_to_notify.append(i[0])
        
    print(users_to_notify)
         
        
    if str(user_id) in users_to_notify:
           print('You are in notify list. Disable')
           #notify_status = True
           return True
    else:
           print('You are not in notify list. Enable') 
           #notify_status = False
           return False
           


############################### Bot ############################################

# /start command --> calls main menu.
def start(bot, update):
    update.message.reply_text(main_menu_message(), parse_mode=ParseMode.HTML,
                           reply_markup=main_menu_keyboard(), timeout=25)


def button_actions(bot, update):
    query = update.callback_query
    
    global current_callback
    global cid
    
    # To know which button was pressed.
    current_callback = query.data
    # To know chat id for notify action.
    cid = query.message.chat_id
    
    print('Button pressed: ', current_callback)

    # Calls main menu.
    if current_callback == 'main_menu':

        bot.edit_message_text(chat_id = query.message.chat_id,
                                message_id = query.message.message_id,
                                text=main_menu_message(),
                                # Used for bold font
                                parse_mode=ParseMode.HTML,
                                reply_markup=main_menu_keyboard(), timeout=25)
                                
    
    # Calls answer with certain timetable depending on the button pressed before.
    if current_callback in  ['answer_p1', 'answer_p2', 'answer_p3', 'answer_p4', 'refresh', 'notify']:

        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=answer_message(),
                        # Used for bold font
                        parse_mode=ParseMode.HTML,
                        reply_markup=answer_keyboard(), timeout=25)
        print(query.message.message_id)
    
    
    # Deletes notification message.
    if current_callback == 'delete_notification':
        bot.delete_message(cid, query.message.message_id)


############################# Messages #########################################

# Main menu text
def main_menu_message():
  
    menu_text = '<b>LFTable</b>: работа с расписанием занятий юридического факультета БГУ.\n\n'
    
    menu_text += 'Источник: https://law.bsu.by\n'
    menu_text += 'Информация об авторских правах юрфака: https://law.bsu.by/avtorskie-prava.html\n'
    
    # To fix badrequest error.
    menu_text += 'Страница обновлена: ' + datetime.now().strftime("%d.%m.%Y %H:%M:%S") + '\n\n'
  
    menu_text += 'Выберите нужное расписание:'

    return(menu_text)


# The message text is formed in accordance with the timetable selected in the main menu.
def answer_message():
    
    # Used for refresh function
    global old_ttb
    
    # Used for notify function
    global cid
    global current_ttb
    
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
    
    # If "notify" button is pressed.
    elif current_callback == 'notify':
        current_ttb = old_ttb
        
        # Disable if user id is already in the db. Delete row from db.
        if check_user_notified(current_ttb, cid):
            conn = sqlite3.connect(users_db)
            cursor = conn.cursor()
        
            cursor.execute('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = \'' + str(cid) + '\')') #304687124');
            result = cursor.fetchall()
            
            # Save changes and close.
            conn.commit()
            conn.close()
         
        # Enable notifying. Insert user id into db.
        else:
            conn = sqlite3.connect(users_db)
            cursor = conn.cursor()
        
            cursor.execute('INSERT INTO ' + current_ttb.shortname + ' VALUES (\'' + str(cid) + '\')')
            result = cursor.fetchall()
            
            # Save changesa and close.
            conn.commit()
            conn.close()
    
        
    # Get the timetable's "mtime"
    ttb_datetime = ttb_gettime(current_ttb)
    
    
    # Change date to necessary format.
    update_time = ttb_datetime.strftime('%H:%M')
    update_date = ttb_datetime.strftime('%d.%m.%Y')
    
    
    # Form the message's text
    answer_text = '<b>' + current_ttb.name + '</b>\n\n'
    
    answer_text += 'Дата обновления: ' + update_date + '\n'
    answer_text += 'Время обновления: '+ update_time + '\n\n'

    answer_text += '<b>СКАЧАТЬ</b>: ' + current_ttb.url + "\n\n"
    
    # To fix badrequest error.
    answer_text += '-------------------\n'
    answer_text += 'Страница обновлена: ' + datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
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
    
    # Used for notify button.
    global current_ttb
    
    # Button to refresh current answer menu (so you don't have to come back to main menu).
    refresh_button = InlineKeyboardButton('🔄 Обновить   ', callback_data='refresh')
    
    # For notify function. Adds info to DB.
    if check_user_notified(current_ttb, cid):
        notify_text = '❌ Не уведомлять'
    else:
        notify_text = '🛎 Уведомлять'
    
    # Button to put user id into db in order to notify him when the timetable is updated. 
    notify_button = InlineKeyboardButton(notify_text, callback_data='notify')
    
 
    # Sends user back to the main menu.
    back_button = InlineKeyboardButton('⬅️ Назад в меню', callback_data='main_menu')

    keyboard = [[refresh_button],
                [notify_button],
                  [back_button]]
                  
    return(InlineKeyboardMarkup(keyboard))



############################# Notify part #########################################


# Keyboard for the message.
def notify_keyboard():
    
    del_notification_button = InlineKeyboardButton('Скрыть',  callback_data='delete_notification')
    
    keyboard = [[del_notification_button]]
    
    return(InlineKeyboardMarkup(keyboard))


# Send message.
def callback_minute(bot, job):
    
    conn_times_db = sqlite3.connect(times_db)
    cursor_times_db = conn_times_db.cursor()
    
    for checking_ttb in [pravo_c1, pravo_c2, pravo_c3, pravo_c4]:
        
        # Get ttb update time from law.bsu.by
        update_time = ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')
        
        print(checking_ttb.shortname, 'updated at: ', update_time)
       
        
        # Get old update time from db.
        cursor_times_db.execute("SELECT time  FROM times WHERE (ttb = ?)", (checking_ttb.shortname,));
        result = cursor_times_db.fetchall()
        old_update_time = result[0][0]
        del(result)
        
        
        # String dates to datetime objects
        dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
        dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')
        
        print('old update time: ', old_update_time)
        
        
        # If the timetable was updated, sends it to all users 
        #+ from certain table in 'users.db'
        if dt_update_time > dt_old_update_time:
            print('TTB WAS UPDATED')
            
            notification_text = 'Появилось расписание <b>"' + checking_ttb.name + '". </b>\n'
            notification_text += 'Дата обновления: ' + dt_update_time.strftime('%d.%m.%Y') + '\n'
            notification_text += 'Время обновления: '+ dt_update_time.strftime('%H:%M') + '\n\n' 
            notification_text += '<b>Скачать</b>: ' + checking_ttb.url + "\n\n"
            
            # Connect to users db.
            conn_users_db = sqlite3.connect(users_db)
            cursor_users_db = conn_users_db.cursor()
        
            cursor_users_db.execute('SELECT users FROM ' + checking_ttb.shortname)
            result = cursor_users_db.fetchall()

            conn_users_db.close()
    
            # List for users notifed about current timetable updates.
            users_to_notify = []
            for i in result:
                users_to_notify.append(i[0])
            del(result)
            
            
            
            # Send notifications to users.
            for user_id in users_to_notify:
                bot.send_message(chat_id=user_id, text=notification_text, reply_markup=notify_keyboard(), parse_mode=ParseMode.HTML)
                time.sleep(3)
                
            
            # Writing new update time to the database.
            cursor_times_db.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (checking_ttb.shortname,));
            conn_times_db.commit()
            
        time.sleep(3)
    
    # Close 'times.db' until next check.
    conn_times_db.close()


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

# Run ttb checks on on schedule (see check_updates_interval in 'static.py'
job = updater.job_queue
job.run_repeating(callback_minute, interval = check_updates_interval, first=0)


# Handlers
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CallbackQueryHandler(button_actions))


# Checking for updates.
updater.start_polling(clean=True)
# Stop bot if  <Ctrl + C> pressed.
updater.idle()
