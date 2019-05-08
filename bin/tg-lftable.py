#!/usr/bin/env python3

import os
import sys
# Add src/' directory with local modules to path
sys.path.append('src')

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ParseMode

from datetime import datetime

import logging
import sqlite3

import time

# Import all local modules, see 'src/' directory to understand how everythong works
from static import *
from messages import *
from backend import *
from keyboards import *

# Writes logging messages to lftable.log file.
# To log all exception you should start the program with '-e'option.
# Exception logger generates a bulk otuput, so the log file (lftable-exceptions.log) may become exctremely large
# That's why this logger is disabled by default
from logger import *


# /start command --> calls main menu.
def start(bot, update):
    update.message.reply_text(main_menu_message(),
                              parse_mode=ParseMode.HTML,
                              reply_markup=main_menu_keyboard(),
                              timeout=25)


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
    if callback in  ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4',
                             'mag_c1', 'mag_c2',
                             'refresh', 'notify']:

        # If any of TTB buttons is pressed
        if callback == 'pravo_c1':
            current_ttb = pravo_c1
        elif callback == 'pravo_c2':
            current_ttb = pravo_c2
        elif callback == 'pravo_c3':
            current_ttb = pravo_c3
        elif callback == 'pravo_c4':
            current_ttb = pravo_c4
        elif callback == 'mag_c1':
            current_ttb = mag_c1
        elif callback == 'mag_c2':
            current_ttb = mag_c2


        # If 'refresh' or 'notify' button is pressed
        elif callback in ['refresh', 'notify']:

            # Detect the timetable checking first line of the ttb message
            message = query.message
            for ttb in all_timetables:

                if message.text.split('\n')[0] == ttb.name:
                    current_ttb = ttb


            if callback == 'notify':

                # Disable if user id is already in the db. Delete row from db.
                if check_user_notified(current_ttb, user_id):
                    conn = sqlite3.connect(notifications_db)
                    cursor = conn.cursor()

                    cursor.execute('DELETE FROM ' + current_ttb.shortname + ' WHERE (users = \'' + str(user_id) + '\')')
                    result = cursor.fetchall()

                    # Save changes and close.
                    conn.commit()
                    conn.close()

                    # Write to log
                    logger.info('user ' + str(user_id) + " disabled notifications for the '" + current_ttb.shortname + "' timetable")

                # Enable notifications. Insert user id into the db.
                else:
                    conn = sqlite3.connect(notifications_db)
                    cursor = conn.cursor()

                    cursor.execute('INSERT INTO ' + current_ttb.shortname + ' VALUES (\'' + str(user_id) + '\')')
                    result = cursor.fetchall()

                    # Save changesa and close.
                    conn.commit()
                    conn.close()

                    # Write to log
                    logger.info('user ' + str(user_id) + " enabled notifications for the '" + current_ttb.shortname + "' timetable")



        # Edit message depending on the callback and current ttb variable
        bot.edit_message_text(chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text=ttb_message(current_ttb),
                        # Used for bold font
                        parse_mode=ParseMode.HTML,
                        reply_markup=answer_keyboard(current_ttb, user_id), timeout=25)


    # Deletes notification message if 'delete' button is pressed.
    if callback == 'delete_notification':
        bot.delete_message(user_id, query.message.message_id)
        # Write to log
        logger.info('user ' + str(user_id) + " deleted notification (message: " + str(query.message.message_id) + ")")



# A timejob for notifications
def notifications_timejob(bot, job):

    # Connect to the times.db
    conn_times_db = sqlite3.connect(times_db)
    cursor_times_db = conn_times_db.cursor()

    # See 'all_timetables' list in 'src/static.py'
    for checking_ttb in all_timetables:

        # Get ttb update time from law.bsu.by
        update_time = ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')

        # Get old update time from db.
        cursor_times_db.execute("SELECT time  FROM times WHERE (ttb = ?)", (checking_ttb.shortname,));
        result = cursor_times_db.fetchall()
        old_update_time = result[0][0]
        del(result)

        # Convert string dates to datetime objects
        dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
        dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')


        # Compare the two dates
        # If the timetable was updated, sends it to all users
        #+ from certain table in 'users.db'
        if dt_update_time > dt_old_update_time:

            # Write to log
            logger.info("'" + checking_ttb.shortname + "' timetable was updated at " + update_time)

            # Connect to users db.
            conn_notifications_db = sqlite3.connect(notifications_db)
            cursor_notifications_db = conn_notifications_db.cursor()

            cursor_notifications_db.execute('SELECT users FROM ' + checking_ttb.shortname)
            result = cursor_notifications_db.fetchall()

            conn_notifications_db.close()

            # List for users notifed about current timetable updates.
            users_to_notify = []
            for i in result:
                users_to_notify.append(i[0])
            del(result)


            # Send a notification to each user.
            for user_id in users_to_notify:

                try:
                    bot.send_message(chat_id=user_id, text=notification_message(checking_ttb, dt_update_time), reply_markup=notify_keyboard(), parse_mode=ParseMode.HTML)
                except Exception as e:
                    # Write to log
                    logger.info("can't send '" + checking_ttb.shortname + "' notification to user " + str(user_id) + ", skip")
                    continue

                # Write to log
                logger.info("'" + checking_ttb.shortname + "' notification was sent to user " + str(user_id))

                # A delay to prevent any spam control exceptions
                time.sleep(send_message_interval)


            # Write new update time to the database.
            cursor_times_db.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (checking_ttb.shortname,));
            conn_times_db.commit()


        # A delay to prevent any spam control exceptions
        time.sleep(send_message_interval)

    # Close 'times.db' until next check.
    conn_times_db.close()



def main():

    # Write 'program started' message to log
    logger.info("the program was STARTED now")

    if not os.path.isfile(tokens_file):
        print('No tokens file ' + tokens_file + '. Exit.')
        sys.exit()

    # Parse arguments
    # Cant start in both dev and release regimes
    if "-r" in sys.argv and "-d" in sys.argv:
        print("Invalid arguments passed. Use '-r' option to run with release token, '-d' - with development token")
        logger.critical("invalid arguments, exit")
        sys.exit()

    # Start woth release token
    if '-r' in sys.argv:
        print("Started in release mode")
        try:
            # See src/tokens.py file
            from tokens import release_token
            token_str = release_token
        except Exception:
            logger.critical("no 'release_token' in tokens.py file, exit")
            print("no 'release_token' in token.py, exit")
            sys.exit()

    # Start with dev token
    if "-d" in sys.argv:
        print("Started in development mode")
        try:
            # See src/tokens.py file
            from tokens import dev_token
            token_str = dev_token
        except Exception:
            logger.critical("no 'dev_token' in tokens.py file, exit")
            print("no 'dev_token' in token.py, exit")
            sys.exit()

    # Log exception
    if '-e' in sys.argv:
        log_exceptions()

    # Create necessary directories and files if don't already exist
    # See 'src/backend.py' file
    first_run_check()
    # Write times to the db after the start  to prevent late notifications.
    db_set_times_after_run()


    updater = Updater(token_str)
    dp = updater.dispatcher

    # Run timejob for notificatins
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
