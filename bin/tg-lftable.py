#!/usr/bin/env python3

import os
import sys
# Add directory with local modules to path
sys.path.append('src')

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode

import urllib.request
from datetime import datetime

import pytz

import logging
import sqlite3

import time

import ssl

# Import all local modules
from static import *
from messages import *
from backend import *
from keyboards import *
from logger import *

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



# Write 'program started' message to log
logger.info("the program was STARTED now")




############################### Bot commands ############################################

# /start command --> calls main menu.
def start(bot, update):
    update.message.reply_text(main_menu_message(), parse_mode=ParseMode.HTML,
                           reply_markup=main_menu_keyboard(), timeout=25)

   
# Bot's behavior depending on the button pressed.
def button_actions(bot, update):


    query = update.callback_query
    
    # To know which button was pressed.
    callback = query.data
    # The user who pressed the button
    user_id = query.message.chat_id
    
    # If a new user joins the bot, this function writes his id to the 'statistics.db'
    send_statistics(user_id)
    
    # Write to log
    logger.debug('user ' + str(user_id) + " pressed button '" + callback + "'")
    

    # Sends main menu.
    if callback == 'main_menu':

        bot.edit_message_text(chat_id = query.message.chat_id,
                                message_id = query.message.message_id,
                                text=main_menu_message(),
                                # Used for bold font
                                parse_mode=ParseMode.HTML,
                                reply_markup=main_menu_keyboard(), timeout=25)
                                
    
    # Sends message with certain timetable info depending on the button pressed before.
    if callback in  ['answer_p1', 'answer_p2', 'answer_p3', 'answer_p4', 
                             'answer_m1', 'answer_m2',
                             'refresh', 'notify']:
        
        if callback == 'answer_p1':
            current_ttb = pravo_c1
        elif callback == 'answer_p2':
            current_ttb = pravo_c2
        elif callback == 'answer_p3':
            current_ttb = pravo_c3
        elif callback == 'answer_p4':
            current_ttb = pravo_c4
    
        elif callback == 'answer_m1':
            current_ttb = mag_c1
        elif callback == 'answer_m2':
            current_ttb = mag_c2
        
        elif callback in ['refresh', 'notify']:

            # Detect the timetable checking first line of the ttb message
            message = query.message
            for ttb in all_timetables:

                if message.text.split('\n')[0] == ttb.name:
                    current_ttb = ttb

            
            if callback == 'notify':

                # Disable if user id is already in the dbs. Delete row from db.
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

        
        
        # Edit message depending on the callback
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=ttb_message(current_ttb),
                        # Used for bold font
                        parse_mode=ParseMode.HTML,
                        reply_markup=answer_keyboard(current_ttb, user_id), timeout=25)

    
    # Deletes notification message.
    if callback == 'delete_notification':
        bot.delete_message(user_id, query.message.message_id)
        # Write to log
        logger.info('user ' + str(user_id) + " deleted notification (message: " + str(query.message.message_id) + ")")
    


# Notification message. 
def notifications_timejob(bot, job):
	
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
                bot.send_message(chat_id=user_id, text=notification_message(checking_ttb, dt_update_time), reply_markup=notify_keyboard(), parse_mode=ParseMode.HTML)
                
                # Write to log
                logger.info("'" + checking_ttb.shortname + "' notification was sent to user " + str(user_id))
                
                time.sleep(send_message_interval)
                
            
            # Writing new update time to the database.
            cursor_times_db.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (checking_ttb.shortname,));
            conn_times_db.commit()
            
        time.sleep(send_message_interval)
    
    # Close 'times.db' until next check.
    conn_times_db.close()
    
    



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
    job.run_repeating(notifications_timejob, interval = check_updates_interval, first=0)
    
    
    # Handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_actions))


    # Checking for updates.
    updater.start_polling(clean=True)
    # Stop bot if  <Ctrl + C> is pressed.
    updater.idle()

    
    
if __name__ == "__main__":
    main()


