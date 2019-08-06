#!/usr/bin/env python3

import os
import sys
import time
import sqlite3
import argparse
from datetime import datetime

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# Import all local modules, see 'src/' directory
import src.db_classes
import src.gettime
import src.static
import src.messages
import src.keyboards

# Logging to 'lftable.log'
# Add '--log-exceptions' option to script to log exceptions ('lftable-exceptions.log')
from src.logger import *


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
    user_id = str(query.message.chat_id)

    # If a new user joins the bot, this function writes his id to the 'statistics.db'
    statisticsdb.connect()
    if user_id not in statisticsdb.get_unique_users():
        statisticsdb.add_uniq_user(user_id)
        logger.info("a new user "  + str(user_id) + " added to 'statistics.db'")
    statisticsdb.close()

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
                notificationsdb.connect()

                # Disable if user id is already in the db. Delete row from db.
                if notificationsdb.check_if_user_notified(user_id, current_ttb.shortname):

                    notificationsdb.disable_notifications(user_id, current_ttb.shortname)
                    notificationsdb.close()

                    # Write to log
                    logger.info('user ' + str(user_id) + " disabled notifications for the '" + current_ttb.shortname + "' timetable")

                # Enable notifications. Insert user id into the db.
                else:

                    notificationsdb.enable_notifications(user_id, current_ttb.shortname)
                    notificationsdb.close()

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
    timesdb.connect()

    # See 'all_timetables' list in 'src/static.py'
    for checking_ttb in all_timetables:

        # Get ttb update time from law.bsu.by
        update_time = src.gettime.ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')

        # Get old update time from db.
        old_update_time = timesdb.get_time(checking_ttb.shortname)


        # Convert string dates to datetime objects
        dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
        dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')


        # Compare the two dates
        # If the timetable was updated, sends it to all users
        #+ from certain table in 'users.db'
        if dt_update_time > dt_old_update_time:

            # Write to log
            logger.info("'" + checking_ttb.shortname + "' timetable was updated at " + update_time)

            notificationsdb.connect()
            users_to_notify = notificationsdb.get_notified_users(checking_ttb.shortname)
            notificationsdb.close()

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
            timesdb.write_time(checking_ttb.shortname, update_time)


        # A delay to prevent any spam control exceptions
        time.sleep(send_message_interval)

    # Close 'times.db' until next check.
    timesdb.close()



def main():

    # Write 'program started' message to log
    logger.info("the program was STARTED now")

    try:
        import src.tokens
    except ImportError:
        print('No tokens file ' + tokens_file + '. Exit.')
        logger.critical("can't import 'tokens.py', exit.")
        sys.exit()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="tg-lftable: telegram bot which provides an easy way to get the law faculty's timetable (BSU).")

    parser.add_argument('--log-exceptions', action='store_true')

    required_arg = parser.add_argument_group(title='required arguments')
    required_arg.add_argument('--mode',
                        type=str,
                        help='Either \'release\' or \'development\' string. The bot starts with the corresponding token',
                        required=True)

    args = parser.parse_args()

    if args.mode == 'release':
        print("Started in 'release' mode")

    elif args.mode == 'develop':
        print("Started in 'develop' mode")

    else:
        print("Invalid mode specified. Use either 'release' or 'develop' string.' Exit.")
        sys.exit()

    # set token_str depending on --mode parameter
    try:
        # see tokens.py module
        token_str = getattr(src.tokens, args.mode)
    except AttributeError:
        logger.critical("no '" + args.mode + "' token string variable in tokens.py file, exit")
        print("no '" + args.mode + "' token string variable in tokens.py file, exit")

    # Log exceptions
    if args.log_exceptions == True:
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


class LFTableBot():
    def __init__(self):

        # Start message
        logger.info("the program was STARTED now")

        # Import src/tokens.py
        try:
            import src.tokens
        except ImportError:
            print('No tokens file. Exit.')
            logger.critical("can't import 'tokens.py', exit.")
            sys.exit()

        # Change directory to the one in wich the script is located
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        self.timesdb = src.db_classes.TimesDB()
        self.notificationsdb = src.db_classes.NotificationsDB()
        self.statisticsdb = src.db_classes.StatisticsDB()

        self.prepare_workspace()
        self.parse_arguments()

    # This method creates necessary directories and files
    def prepare_workspace(self):

        # Create directory for sqlite3 databases
        if not os.path.exists(src.static.db_dir):
            os.mkdir(db_dir)

        # Create databases. See db_classes.py
        if not os.path.isfile(src.static.times_db):
            self.timesdb.connect()
            self.timesdb.construct()
            self.timesdb.close()

            logger.info("'" + src.static.times_db + "' database was created")

        if not os.path.isfile(src.static.notifications_db):
            self.notificationsdb.connect()
            self.notificationsdb.construct()
            self.notificationsdb.close()

            logger.info("'" + src.static.notifications_db + "' database was created")

        if not os.path.isfile(src.static.statistics_db):
            self.statisticsdb.connect()
            self.statisticsdb.construct()
            self.statisticsdb.close()

            logger.info("'" + src.static.statistics_db + "' database was created")

    # Parse command-line arguments
    def parse_arguments(self):

        parser = argparse.ArgumentParser(description="tg-lftable: telegram bot which provides an easy way to get the law faculty's timetable (BSU).")

        parser.add_argument('--log-exceptions', action='store_true')

        required_arg = parser.add_argument_group(title='required arguments')
        required_arg.add_argument('--mode',
                                  type=str,
                                  help='Either \'release\' or \'development\' string. The bot starts with the corresponding token',
                                  required=True)

        args = parser.parse_args()

        if args.mode == 'release':
            print("Started in 'release' mode")

        elif args.mode == 'develop':
            print("Started in 'develop' mode")

        else:
            print("Invalid mode specified. Use either 'release' or 'develop' string.' Exit.")
            sys.exit()

        # get token depending on --mode parameter
        try:
            self.bot_token = getattr(src.tokens, args.mode)
        except AttributeError:
            logger.critical("no '" + args.mode + "' token string variable in tokens.py file, exit")
            print("no '" + args.mode + "' token string variable in tokens.py file, exit")

        # Log exceptions
        if args.log_exceptions == True:
            log_exceptions()


    # Sends main menu on '/start' command
    def handle_start_command(self, bot, update):
        update.message.reply_text(src.messages.main_menu_message(),
                                  reply_markup=src.keyboards.main_menu_keyboard(),
                                  parse_mode=ParseMode.HTML,
                                  timeout=10)


    def start(self):
        # Sets times to the 'times.db' immediately after the run WITHOUT notifiying users
        # This is to prevent late notifications if the bot was down for a long time
        self.timesdb.connect()
        for timetable in src.static.all_timetables:
            update_time = src.gettime.ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')
            self.timesdb.write_time(timetable.shortname, update_time)
        self.timesdb.close()


        self.updater = Updater(self.bot_token)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler('start', self.handle_start_command))
        self.dispatcher.add_handler(CallbackQueryHandler(self.handle_button_click))

        # Checking for updates.
        self.updater.start_polling(clean=False)
        self.updater.idle()


if __name__ == "__main__":
    #main()
    lftable = LFTableBot()
    lftable.start()
