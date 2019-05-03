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

import ssl

# See static.py to understant how it works.
# This file contains app version, TTBS objects, their attributes, paths to databases and token files. 
from static import *
from messages import *

# Global variables
# Used for refresh function
old_ttb = None
# Used for notify function
notify_status = None
current_ttb = None


######################## Logging settings ##############################

# Nothing will work without logging
if not os.path.exists('log/'):
    try:
        os.mkdir('log/')
    except Exception:
        print("CRITICAL ERROR: can't create 'log/' directory. Exit")
        sys.exit()


# Uncomment this and see 'log/lftable-exceptions.log' if something goes wrong.
#"""
# Logger for all exceptions.
logging.basicConfig(filename=log_dir + "lftable-exceptions.log", level=logging.DEBUG)
exception_logger = logging.getLogger('exception_logger')

# Install exception handler
def my_handler(type, value, tb):
    exception_logger.exception("Uncaught exception: {0}".format(str(value)))
sys.excepthook = my_handler
#"""

# A simple logger
#logging_filename = log_dir + 'lftable-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.log'
logging_filename = log_dir + 'lftable.log'

logger = logging.getLogger('lftable')
logger.setLevel(logging.DEBUG)

filehandler = logging.FileHandler(filename=logging_filename)
filehandler.setFormatter(logging.Formatter('%(filename)s [LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'))
logger.addHandler(filehandler)

# Write 'program started' message to log
logger.info("the program was STARTED now")

########################################################################

# The most important function of the program.
# Get and return timetable's mtime using urllib module. 
def ttb_gettime(ttb):
    

    # THIS IS A HOTFIX TO PREVENT "CERTIFICATE_VERIFY_FAILED" ERROR!
    # DISABLE THIS LATER
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    response =  urllib.request.urlopen(ttb.url, timeout=25, context=ctx)
    
    # Get date from HTTP header.
    native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
    
    # Transfer date to normal format.
    gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')
    
    # Transfer date to our timezone (GMT+3).
    old_tz = pytz.timezone('Europe/London')
    new_tz = pytz.timezone('Europe/Minsk')
    
    date = old_tz.localize(gmt_date).astimezone(new_tz) 
    
    return(date)


########################################################################
########################################################################

# Create necessary project dirs and files.
# (See 'static.py' for values of the variables)
def first_run_check():
    
    try:
        os.mkdir(db_dir)
        # Write to log
        logger.info("'" + db_dir + "' directory was created")
    except Exception:
        pass
        
    try:
        os.mkdir(tokens_dir)
        # Write to log
        logger.info("'" + tokens_dir + "' directory was created")
    except Exception:
        pass  
 
 
    # Create database for users notified about timetables' updates.
    # 4 tables for each timetable, each with 'users' column
    if not os.path.exists(users_db):
        conn = sqlite3.connect(users_db)
        cursor = conn.cursor()   
        
        # Write to log
        logger.info("'" + users_db + "' database was created")
        
        for timetable in all_timetables:
            cursor.execute('CREATE TABLE ' + timetable.shortname + ' (users)')
            
        conn.commit()
        conn.close()
        
        
    # Create database to store the last update time of each timetable
    # 1 table, 4 rows (1 for each timetable), 2 columns (ttb name and the time of last update)
    if not os.path.exists(times_db):
        
        conn = sqlite3.connect(times_db)
        cursor = conn.cursor()
        
        # Write to log
        logger.info("'" + times_db + "' database was created")
        
        cursor.execute('CREATE TABLE times (ttb, time)')
        conn.commit()
        
        for timetable in all_timetables:
            cursor.execute('INSERT INTO times VALUES ("' + timetable.shortname + '", "")')
        
        conn.commit()
        conn.close()
    
    
    # Database for statistics.
    if not os.path.exists(statistics_db):
        conn = sqlite3.connect(statistics_db)
        
        # Write to log
        logger.info("'" + statistics_db + "' database was created")
        
        cursor = conn.cursor()
        
        cursor.execute('CREATE TABLE uniq_users (users)')
        
        conn.commit()
        conn.close()

########################################################################

# Sets times to the 'times.db' immediately after the run WITHOUT notifiying users 
# Prevents late notifications if the program was down for a long time.
def db_set_times_after_run():
    conn = sqlite3.connect(times_db)
    cursor = conn.cursor()
    
    for timetable in all_timetables:
        
        update_time = ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')
        
        cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (timetable.shortname,));
        
    conn.commit()
    conn.close()

    
        
########################################################################        
# Collecting statistics.
# Writes uniq user ids to 'statistics.db'
def send_statistics(user_id):
    conn = sqlite3.connect(statistics_db)
    cursor = conn.cursor()
        
    cursor.execute('SELECT * FROM uniq_users')
    result = cursor.fetchall()

    # List of user_ids in the db
    uniq_users = []
    for i in result:
        uniq_users.append(i[0])
    
    # Add new user to the db
    if user_id not in uniq_users:
        cursor.execute('INSERT INTO uniq_users VALUES (?)', (user_id,))
        conn.commit()
        # Write to log
        logger.info("a new user "  + str(user_id) + " added to 'statistics.db'")
        
    conn.close()

########################################################################

# NOTIFICATIONS.
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
        
        
    if str(user_id) in users_to_notify:
           return True
    else:
           return False



############################### Bot commands ############################################

# /start command --> calls main menu.
def start(bot, update):
    update.message.reply_text(main_menu_message(), parse_mode=ParseMode.HTML,
                           reply_markup=main_menu_keyboard(), timeout=25)

   
# Bot's behavior depending on the button pressed.
def button_actions(bot, update):
    query = update.callback_query
    
    # The button pressed.
    global current_callback
    # The user who pressed the button
    global user_id
    
    
    # To know which button was pressed.
    current_callback = query.data
    # To know chat id for notify action.
    user_id = query.message.chat_id
    
    # If a new user joins the bot, this function writes his id to the 'statistics.db'
    send_statistics(user_id)
    
    
    #print('Button pressed: ', current_callback)
    # Write to log
    logger.debug('user ' + str(user_id) + " pressed button '" + current_callback + "'")
    

    # Calls main menu.
    if current_callback == 'main_menu':

        bot.edit_message_text(chat_id = query.message.chat_id,
                                message_id = query.message.message_id,
                                text=main_menu_message(),
                                # Used for bold font
                                parse_mode=ParseMode.HTML,
                                reply_markup=main_menu_keyboard(), timeout=25)
                                
    
    # Calls answer with certain timetable depending on the button pressed before.
    if current_callback in  ['answer_p1', 'answer_p2', 'answer_p3', 'answer_p4', 
                             'answer_m1', 'answer_m2',
                             'refresh', 'notify']:
        
        if current_callback == 'notify':
            # Disable if user id is already in the db. Delete row from db.
            if check_user_notified(current_ttb, user_id):
                conn = sqlite3.connect(users_db)
                cursor = conn.cursor()
        
                cursor.execute('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = \'' + str(user_id) + '\')')
                result = cursor.fetchall()
            
                # Save changes and close.
                conn.commit()
                conn.close()
            
                # Write to log
                logger.info('user ' + str(user_id) + " disabled notifications for the '" + current_ttb.shortname + "' timetable")
                    
            # Enable notifying. Insert user id into db.
            else:
                conn = sqlite3.connect(users_db)
                cursor = conn.cursor()
        
                cursor.execute('INSERT INTO ' + current_ttb.shortname + ' VALUES (\'' + str(user_id) + '\')')
                result = cursor.fetchall()
            
                # Save changesa and close.
                conn.commit()
                conn.close()
                
                # Write to log
                logger.info('user ' + str(user_id) + " enabled notifications for the '" + current_ttb.shortname + "' timetable")
        
        
        
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=answer_message(),
                        # Used for bold font
                        parse_mode=ParseMode.HTML,
                        reply_markup=answer_keyboard(), timeout=25)
    
    
    # Deletes notification message.
    if current_callback == 'delete_notification':
        bot.delete_message(user_id, query.message.message_id)
        # Write to log
        logger.info('user ' + str(user_id) + " deleted notification (message: " + str(query.message.message_id) + ")")


# The message for a certain timetable.
# The message text is formed in accordance with the timetable selected in the main menu.
def answer_message():
    
    # Used for refresh function
    global old_ttb
    
    # Used for notify function
    global user_id
    global current_ttb
    
    if current_callback == 'answer_p1':
        current_ttb = pravo_c1
    elif current_callback == 'answer_p2':
        current_ttb = pravo_c2
    elif current_callback == 'answer_p3':
        current_ttb = pravo_c3
    elif current_callback == 'answer_p4':
        current_ttb = pravo_c4
    
    elif current_callback == 'answer_m1':
        current_ttb = mag_c1
    elif current_callback == 'answer_m2':
        current_ttb = mag_c2
        
    elif current_callback == 'refresh':
        current_ttb = old_ttb
    
    elif current_callback == 'notify':
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

    answer_text += '<b>Скачать</b>: ' + current_ttb.url + "\n\n"
    
    # To fix badrequest error.
    answer_text += '-------------------\n'
    answer_text += 'Страница обновлена: ' + datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    
    # For 'refresh' function.
    old_ttb = current_ttb
    
    # Return this text
    return(answer_text)
    

# Notification message. 
def callback_minute(bot, job):
    
    conn_times_db = sqlite3.connect(times_db)
    cursor_times_db = conn_times_db.cursor()
    
    for checking_ttb in all_timetables:
        
        # Get ttb update time from law.bsu.by
        update_time = ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')
        
        
        # Get old update time from db.
        cursor_times_db.execute("SELECT time  FROM times WHERE (ttb = ?)", (checking_ttb.shortname,));
        result = cursor_times_db.fetchall()
        old_update_time = result[0][0]
        del(result)
        
        
        # String dates to datetime objects
        dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
        dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')
        
        
        # If the timetable was updated, sends it to all users 
        #+ from certain table in 'users.db'
        if dt_update_time > dt_old_update_time:
            
            # Write to log
            logger.info("'" + checking_ttb.shortname + "' timetable was updated at " + update_time)

            notification_text = '🔔 Обновлено расписание <b>"' + checking_ttb.name + '". 🔔</b>\n'
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
                
                # Write to log
                logger.info("'" + checking_ttb.shortname + "' notification was sent to user " + str(user_id))
                
                time.sleep(send_message_interval)
                
            
            # Writing new update time to the database.
            cursor_times_db.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (checking_ttb.shortname,));
            conn_times_db.commit()
            
        time.sleep(send_message_interval)
    
    # Close 'times.db' until next check.
    conn_times_db.close()
    
    
############################ Keyboards #########################################

# Main menu keyboard.
# 4 buttons in main menu. Each button is designed for the corresponding timetable (1-4 course)
def main_menu_keyboard():
    
    pravo_c1.btn = InlineKeyboardButton('Правоведение - 1⃣', callback_data='answer_p1')
    pravo_c2.btn = InlineKeyboardButton('Правоведение - 2⃣', callback_data='answer_p2')
    pravo_c3.btn = InlineKeyboardButton('Правоведение - 3⃣', callback_data='answer_p3')
    pravo_c4.btn = InlineKeyboardButton('Правоведение - 4⃣', callback_data='answer_p4')

    mag_c1.btn = InlineKeyboardButton('Магистратура - 1⃣', callback_data='answer_m1')
    mag_c2.btn = InlineKeyboardButton('Магистратура - 2⃣', callback_data='answer_m2')
    
    keyboard = [[pravo_c1.btn, pravo_c2.btn],
                [pravo_c3.btn, pravo_c4.btn],
                [mag_c1.btn, mag_c2.btn]]           
          
    return(InlineKeyboardMarkup(keyboard))



# Menu for specific timetable. One button returns to main menu, one refreshes date and time info.
def answer_keyboard():
    
    # Used for notify button.
    global current_ttb
    
    # Button to refresh current answer menu (so you don't have to come back to main menu).
    refresh_button = InlineKeyboardButton('🔄 Обновить страницу', callback_data='refresh')
    
    # For notify function. Adds info to DB.
    if check_user_notified(current_ttb, user_id):
        notify_text = u'🔕 Не уведомлять'
    else:
        notify_text = u'🔔 Уведомлять'
    
    # Button to put user id into db in order to notify him when the timetable is updated. 
    notify_button = InlineKeyboardButton(notify_text, callback_data='notify')
    
 
    # Sends user back to the main menu.
    back_button = InlineKeyboardButton('⬅️ Назад в меню', callback_data='main_menu')

    keyboard = [[refresh_button],
                [notify_button],
                  [back_button]]
                  
    return(InlineKeyboardMarkup(keyboard))


# Keyboard for notification. Only one button to delete message.
def notify_keyboard():
    
    del_notification_button = InlineKeyboardButton('Скрыть уведомление',  callback_data='delete_notification')
    
    keyboard = [[del_notification_button]]
    
    return(InlineKeyboardMarkup(keyboard))



############################# Bot settings #############################

def main():
     
    
    if len(sys.argv) != 2:
        print("Invalid arguments passed. Use '-r' option to run with release token, '-d' - to run with development token")
        logger.critical("invalid arguments, exit")
        sys.exit()
    
    # See token.py
    if sys.argv[1] == "-r":
        print("Started in release mode")
        try:
            from tokens import release_token
            token_str = release_token
        except Exception:
            logger.critical("no 'release_token' in tokens.py file, exit")
            print("no 'release_token' in token.py, exit")
        
    elif sys.argv[1] == "-d":
        print("Started in development mode")
        try:
            from tokens import dev_token
            token_str = dev_token
        except Exception:
            logger.critical("no 'dev_token' in tokens.py file, exit")
            print("no 'dev_token' in token.py, exit")
   
    else:
        print("Invalid arguments passed. Use '-r' option to run with release token, '-d' - with development token")
        logger.critical("invalid arguments, exit")
        sys.exit()
        

    
    # Create directories and files.
    first_run_check()
    # Write times to the db after the start 
    # to prevent late notifications.
    db_set_times_after_run()
    
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
    # Stop bot if  <Ctrl + C> is pressed.
    updater.idle()

    
    
if __name__ == "__main__":
    main()


